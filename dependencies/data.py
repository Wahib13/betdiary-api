import logging
import os

import motor.motor_asyncio
from bson import ObjectId
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import APIKeyHeader
from jose import jwt, JWTError
from starlette import status

from auth_utils import create_access_token
from models import BetInfo, User, TokenData

logger = logging.getLogger(__name__)

MONGO_STR = f'mongodb://{os.environ.get("MONGO_INITDB_USER")}:' \
            f'{os.environ.get("MONGO_INITDB_PWD")}@{os.environ.get("MONGO_HOST")}:27017/' \
            f'{os.environ.get("MONGO_INITDB_DATABASE_PROJECT")}' \
            f'?authSource=admin&retryWrites=true&w=majority'

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_STR)
db = client.get_default_database()
bet_info_collection = db['bet_info']
users_collection = db['users']

api_key_header_scheme = APIKeyHeader(name='Token')


async def query_bet_infos(limit: int = 10):
    return await bet_info_collection.find().to_list(limit)


async def query_bet_info(omc_id: str):
    try:
        omc = await bet_info_collection.find_one({"_id": ObjectId(omc_id)})
        return omc
    except:
        logger.exception(f'failed to query OMC with id: {omc_id}')


async def query_bet_info_via_fields(query_fields: dict):
    try:
        omc = await bet_info_collection.find_one(query_fields)
        return omc
    except:
        logger.exception(f'failed to query OMC with query fields: {query_fields}')


async def update_bet_info(omc_id: str, new_values: dict):
    try:
        omc = await bet_info_collection.update_one({"_id": ObjectId(omc_id)}, {"$set": new_values})
        return omc
    except:
        logger.exception(f'failed to query OMC with id: {omc_id}')


async def delete_other_bet_info(job_id: str):
    """
    deletes all bet_info records that are not on the given job_id
    :param job_id:
    :return:
    """
    try:
        await bet_info_collection.delete_many({"job_id": {"$ne": job_id}})
    except:
        logger.exception(f'failed to delete other jobs apart from job_id: {job_id}')


async def create_bet_info(omc: BetInfo):
    omc = jsonable_encoder(omc)
    new_omc = await bet_info_collection.insert_one(omc)
    created_omc = await bet_info_collection.find_one({"_id": new_omc.inserted_id})
    return created_omc


async def delete_bet_info(_id: str):
    delete_result = await bet_info_collection.delete_one({"_id": ObjectId(_id)})
    return delete_result.deleted_count


# user data
async def query_user(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=[os.environ.get("ALGORITHM")])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = await users_collection.find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    return user


async def create_user(user: User):
    user = jsonable_encoder(user)
    new_user = await users_collection.insert_one(user)
    created_user = await users_collection.find_one({"_id": new_user.inserted_id})
    create_access_token({"email": created_user.get("email")})
    return created_user


async def get_authenticated_user(token: str = Depends(api_key_header_scheme)):
    print(token)
    user = await query_user(token)
    if user:
        return User.parse_obj(user)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid token')


async def get_authenticated_super_user(authenticated_user: User = Depends(get_authenticated_user)):
    if authenticated_user.super_user:
        return authenticated_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='forbidden')
