import yaml
import jwt
import datetime
from fastapi import HTTPException
import bcrypt
import numpy as np
import face_recognition
import io
import utils.constants as constants
from database_connections.DatabaseConnectionFactory import DatabaseConnectionFactory

def read_secret_credentials():
    try:
        with open(constants.CREDENTIALS_YAML_PATH, 'r') as f:
            creds = yaml.load(f, yaml.Loader)
            return creds['rest_api']
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except KeyError:
        raise HTTPException(status_code=400, detail="Key not found in file")
    except ValueError:
        raise HTTPException(status_code=500, detail="Unexpected server error.")
    except AttributeError:
        raise HTTPException(status_code=500, detail="Unexpected server error.")
    except NameError:
        raise HTTPException(status_code=500, detail="Unexpected server error.")

def register_user(email, password, first_name, last_name, facial_image):
    credentials = read_secret_credentials()

    #Validation
    if credentials is None \
            or ('secret_token' not in credentials.keys())\
            or ('register_query' not in credentials.keys()):
        raise HTTPException(status_code=400, detail="Key not found in file")

    if type(email) != str or email == '' or email == None \
            or type(password) != str or password == '' or password == None \
            or type(first_name) != str or first_name == '' or first_name == None \
            or type(last_name) != str or last_name == '' or last_name == None:
        raise HTTPException(status_code=400, detail="Bad login parameters.")
    
    image_bytes = facial_image.file.read()
    image = face_recognition.load_image_file(io.BytesIO(image_bytes))
    facial_features = face_recognition.face_encodings(image)[0]

    postgres_connection = DatabaseConnectionFactory().get_connection('postgres')

    user_password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
    user_password = user_password.decode('utf-8')

    query = credentials['register_query'].format(email=email, 
                                                 password=user_password,
                                                 first_name=first_name,
                                                 last_name=last_name,
                                                 facial_features=facial_features
                                                 )
    
    postgres_connection.insert(query)

    return {
        'response':'User registered succesfully!'
    }

def encode_jwt_token(email, password, facial_image):
    credentials = read_secret_credentials()

    #Validation
    if credentials is None \
            or ('secret_token' not in credentials.keys())\
            or ('login_query' not in credentials.keys()):
        raise HTTPException(status_code=400, detail="Key not found in file")

    if type(email) != str or email == '' or email == None \
            or type(password) != str or password == '' or password == None:
        raise HTTPException(status_code=400, detail="Bad login parameters.")
    
    #Image recognition
    image_bytes = facial_image.file.read()
    image = face_recognition.load_image_file(io.BytesIO(image_bytes))
    face_encodings_list = face_recognition.face_encodings(image) 
    print(face_encodings_list)
    if len(face_encodings_list)>0:
        facial_features = face_encodings_list[0]
    else:
        print('E DE AICI')
        raise HTTPException(status_code=401, detail="Invalid credentials. User not recognized in photo!")


    #Query DB by user email
    postgres_connection = DatabaseConnectionFactory().get_connection('postgres')

    query = credentials['login_query'].format(email=email)
    user = postgres_connection.query(query)

    if len(user)!=1:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    #Check if passwords match
    hashed_password = user[0][1].encode('utf-8')
    check_password = bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    if not check_password:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    #Facial Recognition
    db_facial_features = np.fromstring(user[0][2][1:-1], sep= ' ')
    facial_recognition_results = face_recognition.compare_faces([facial_features], db_facial_features)
    print(f'Facial recognition results: {facial_recognition_results}')
    if not facial_recognition_results[0]:
        raise HTTPException(status_code=401, detail="Invalid credentials. User not recognized in photo!")

    #Generate JWT
    now = datetime.datetime.now()
    expiration = now + datetime.timedelta(hours=6)
    try:

        encoded_jwt = jwt.encode({
            'email': email,
            'password': password,
            'exp': expiration.timestamp()
        }, credentials['secret_token'], algorithm="HS256")
        return {
            'token': encoded_jwt
        }
    except TypeError as e:
        raise HTTPException(status_code=400, detail=f"Failed to encode token: {e}")


def decode_jwt_token(token):
    try:
        secret_token = read_secret_credentials()['secret_token']
        decoded = jwt.decode(token, secret_token, algorithms=['HS256'])
        now = datetime.datetime.now().timestamp()
        if 'exp' not in decoded.keys() or decoded['exp'] < now:
            raise HTTPException(status_code=401, detail="Token has expired.")
        return decoded
    except jwt.exceptions.InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid token.")
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except KeyError:
        raise HTTPException(status_code=400, detail="Key not found in file")
