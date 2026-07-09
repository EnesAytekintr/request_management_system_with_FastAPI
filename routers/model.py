from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
from models import ai_model
from starlette import status
from routers.auth import db_dependency, user_dependency
from sqlalchemy import select
router = APIRouter(
    prefix="/model",
    tags=["model"]
)

class ModelRequest(BaseModel):
    model_name: str


@router.get("/", status_code=status.HTTP_200_OK)
async def get_models(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=403, detail="Authentication failed.")

    query = select(ai_model)
    result_raw = await db.execute(query)
    result = result_raw.scalars().all()

    if not result:
        raise HTTPException(status_code=404, detail="There is no ai model.")

    return result

@router.get("/{model_id}", status_code=status.HTTP_200_OK)
async def get_model(user: user_dependency, db: db_dependency, model_id: int = Path(gt=0)):

    query = select(ai_model).filter(ai_model.modelID == model_id)
    result_raw = await db.execute(query)
    result = result_raw.scalars().first()

    if not user:
        raise HTTPException(status_code=403, detail="Authentication failed.")

    if not result:
        raise HTTPException(status_code=404, detail="Model not found")

    return result

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_model(user: user_dependency, model_request: ModelRequest, db: db_dependency):

    if not user:
        raise HTTPException(status_code=403, detail="Authentication failed.")

    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required.")

    model_model = ai_model(**model_request.model_dump())

    db.add(model_model)
    await db.commit()