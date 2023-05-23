from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from api_helper.authentification_helper import decode_jwt_token
from database_connections.DatabaseConnectionFactory import DatabaseConnectionFactory
from typing import Optional
from fastapi import FastAPI, File, Form, UploadFile
import bcrypt
import face_recognition
import io


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token/")

query_route = APIRouter()


@query_route.get("/application", status_code=200)
async def application(token: str = Depends(oauth2_scheme),
                                           country: str = ''):
    decoded = decode_jwt_token(token)
    if decoded is None or decoded == '':
        raise HTTPException(status_code=401, detail="User not logged in.")
    print(decoded)

    postgres_connection = DatabaseConnectionFactory().get_connection('postgres')

    users = postgres_connection.query("Select email, first_name, last_name, facial_features from users")

    return users

@query_route.post("/update_photo", status_code=200)
async def update_photo(token: str = Depends(oauth2_scheme),
    email: Optional[str] = Form(default=None),
    password: Optional[str] = Form(default=None),
    first_name: Optional[str] = Form(default=None),
    last_name: Optional[str] = Form(default=None),
    facial_image: Optional[UploadFile] = File(default=None)
):
    query = ''
    if email:
        query+=f"email = '{email}',"
    if password:
        user_password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        user_password = user_password.decode('utf-8')       
        query+=f"password = '{user_password}',"
    if first_name:
        query+=f"first_name = '{first_name}',"
    if last_name:
        query+=f"last_name = '{last_name}',"
    if facial_image:
        image_bytes = facial_image.file.read()
        image = face_recognition.load_image_file(io.BytesIO(image_bytes))
        facial_features = face_recognition.face_encodings(image)[0]
        query+=f"facial_features = '{facial_features}',"
    
    query = query[:-1]
    decoded = decode_jwt_token(token)
    if decoded is None or decoded == '':
        raise HTTPException(status_code=401, detail="User not logged in.")
    print(decoded)

    postgres_connection = DatabaseConnectionFactory().get_connection('postgres')

    postgres_connection.update_facial_encodings(f"update users set {query} where email = '{decoded['email']}'")

    return {"response":"User updated!"}


