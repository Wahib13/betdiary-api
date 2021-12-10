import os
from datetime import timedelta, datetime
from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from models import User

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    # to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ.get("SECRET_KEY"), algorithm=os.environ.get("ALGORITHM"))
    return encoded_jwt
