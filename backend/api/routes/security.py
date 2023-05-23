from fastapi import APIRouter, File, UploadFile,Form
from api_helper.authentification_helper import encode_jwt_token, register_user

security_route = APIRouter()


@security_route.post('/login', status_code=200)
async def generate_token(email: str = Form(),
                        password: str = Form(),
                        facial_image: UploadFile = File()
                        ):
    gen_token = encode_jwt_token(email, password, facial_image)
    return gen_token

@security_route.post('/register', status_code=200)
async def register_new_user(email: str = Form(),
                            password: str = Form(),
                            first_name: str = Form(),
                            last_name: str = Form(),
                            facial_image: UploadFile = File()
                        ):
    res = register_user(email, password, first_name, last_name, facial_image)
    return res