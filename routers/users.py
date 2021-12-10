from fastapi import APIRouter, Depends

from dependencies import data
from dependencies.data import get_authenticated_super_user
from models import User

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


# @router.post("", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(fake_users_db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

@router.post("/", response_model=User)
async def create_user(user: User, current_user: User = Depends(get_authenticated_super_user)):
    user = await data.create_user(user)
    return user
