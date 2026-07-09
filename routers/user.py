from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field, ConfigDict
from starlette import status
from models import users
from passlib.context import CryptContext
from sqlalchemy import select
from routers.auth import db_dependency, user_dependency

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated= "auto")

class UserRequest(BaseModel):
    user_name: str = Field(min_length=4)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    current_password: str
    new_password: str = Field(min_length=8)

class SubscribeRequest(BaseModel):
    subscription: bool

class UserResponse(BaseModel):
    userID: int
    user_name: str
    first_name: str
    last_name: str
    is_active: bool
    subscription: bool

    model_config = ConfigDict(from_attributes=True)

@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model= UserResponse)
async def get_user(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):

    if not user.get("userID") == user_id:
        raise HTTPException(status_code=403, detail="You can only view your own profile.")

    query = select(users).filter(users.userID == user_id)
    result_raw = await db.execute(query)
    result = result_raw.scalars().first()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.put("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user: user_dependency, db: db_dependency, user_req: UserRequest, user_id: int = Path(gt=0)):

    if user.get("userID") != user_id:
        raise HTTPException(status_code=403, detail="You can only update your profile.")

    query = select(users).filter(users.userID == user_id)
    result_raw = await db.execute(query)
    user_model = result_raw.scalars().first()

    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt_context.verify(user_req.current_password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is invalid.")

    user_model.user_name = user_req.user_name
    user_model.first_name = user_req.first_name
    user_model.last_name = user_req.last_name
    user_model.hashed_password = bcrypt_context.hash(user_req.new_password)

    db.add(user_model)
    await db.commit()


@router.put("/{user_id}/subscribe", status_code= status.HTTP_204_NO_CONTENT)
async def subscribe(user: user_dependency, db: db_dependency, subs_req: SubscribeRequest, user_id: int = Path(gt=0)):

    query = select(users).filter(users.userID == user_id)
    result_raw = await db.execute(query)
    user_model = result_raw.scalars().first()

    if not user.get("userID") == user_id:
        raise HTTPException(status_code=403, detail="You can only update your own subscription.")

    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    user_model.subscription = subs_req.subscription

    db.add(user_model)
    await db.commit()








