import os
from datetime import timedelta, timezone, datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.orm import Session
from database import AsyncSessionLocal
from jose import jwt, JWTError
from sqlalchemy.exc import IntegrityError
import models
from models import users
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated ="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

db_dependency = Annotated[AsyncSession, Depends(get_db)]


async def authenticate_user(user_name: str, password: str, db: db_dependency):
    sorgu = select(users).filter(users.user_name == user_name)
    result_raw = await db.execute(sorgu)
    user = result_raw.scalars().first()

    if not user:
        return None
    if not bcrypt_context.verify(password, user.hashed_password):
        return None
    if not user.is_active:
        return None

    return user

class CreateUserRequest(BaseModel):
    user_name: str = Field(min_length=4)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    password: str = Field(min_length=8)

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(userID: int, user_name: str, is_admin: bool, expires_delta: timedelta):
    expires = datetime.now(timezone.utc) + expires_delta
    encode = {"userID": userID, "user_name": user_name, "is_admin": is_admin, "exp":int(expires.timestamp())}

    return jwt.encode(encode, SECRET_KEY, ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms= [ALGORITHM])
        userID = payload.get("userID")
        user_name = payload.get("user_name")
        is_admin = payload.get("is_admin")

        if not userID or not user_name:
            raise HTTPException(status_code=401, detail="Could not validate user.")

        return {"userID": userID, "user_name": user_name, "is_admin": is_admin}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")


user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = users(
        user_name = create_user_request.user_name,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active= True,
        subscription = False,
        is_admin = False
    )

    db.add(create_user_model)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user name already exists.")

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = await authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")

    token = create_access_token(user.userID, user.user_name, user.is_admin, expires_delta= timedelta(hours=2))

    return {"access_token": token, "token_type": "bearer"}

