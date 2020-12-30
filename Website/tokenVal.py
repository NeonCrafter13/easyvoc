import os
from time import time
import jwt
from db import userdb

from dotenv import load_dotenv
load_dotenv(dotenv_path=".envvar")

SECRET_KEY = os.getenv("email_auth_key")

def get_reset_password_token(user, expires_in=600):
    return jwt.encode(
        {'reset_password': userdb.Get_User_Email(user)[0], 'exp': time() + expires_in},
        SECRET_KEY, algorithm='HS256').decode('utf-8')

def verify_reset_password_token(token):
    try:
        id = jwt.decode(token, SECRET_KEY,
                        algorithms=['HS256'])['reset_password']
    except:
        return
    return userdb.Get_User_id(id)

def get_authentication_token(user, expires_in=600):
    return jwt.encode(
        {'authentication': user[0], 'exp': time() + expires_in},
        SECRET_KEY, algorithm='HS256').decode('utf-8')

def verify_authentication_token(token):
    try:
        id = jwt.decode(token, SECRET_KEY,
                        algorithms=['HS256'])['authentication']
    except:
        return None
    return userdb.Get_User_id(id)
