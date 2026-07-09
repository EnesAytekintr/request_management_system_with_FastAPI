from fastapi import APIRouter, Path, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import joinedload
from models import requests
import models
from sqlalchemy import select
from routers.auth import db_dependency, user_dependency

router = APIRouter(
    prefix="/request",
    tags=["request"]
)

class RequestsRequest(BaseModel):
    modelID: int = Field(gt=0)
    input_text: str = Field(min_length=1)



@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_requests(user: user_dependency,db: db_dependency):

    query = (
        select(requests)
        .options(
            joinedload(requests.input),
            joinedload(requests.output),
            joinedload(requests.model)
        )
        .filter(requests.userID == user.get("userID"))
    )
    result_raw = await db.execute(query)
    result = result_raw.scalars().all()

    if not result:
        raise HTTPException(status_code=404, detail="There is no request.")

    formatted_result = []

    for req in result:

        model_name = req.model.model_name if req.model else "Deleted Model"

        formatted_result.append(
            {
             "requestID": req.requestID,
             "userID": req.userID,
             "model_name": model_name,
             "input_text": req.input.input_text if req.input else None,
             "output_text": req.output.output_text if req.output else None
            }
        )

    return formatted_result


@router.get("/{request_id}", status_code=status.HTTP_200_OK)
async def get_request(user: user_dependency, db: db_dependency,request_id: int = Path(gt=0)):
    query = (
        select(requests)
        .options(
            joinedload(requests.input),
            joinedload(requests.output),
            joinedload(requests.model)
        )
        .filter(requests.requestID == request_id)
    )
    result_raw = await db.execute(query)
    result = result_raw.scalars().first()

    if not result:
        raise HTTPException(status_code=404, detail="Request does not exist.")

    if not result.userID == user.get("userID"):
        raise HTTPException(status_code=403, detail="You do not have access to this request.")

    model_name = result.model.model_name if result.model else "Deleted Model"

    return {"Model": model_name,"Input": result.input.input_text, "Output": result.output.output_text}


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_request(user: user_dependency, db: db_dependency, request_id: int = Path(gt=0)):

    query = select(requests).filter(requests.requestID == request_id)
    result_raw = await db.execute(query)
    result = result_raw.scalars().first()

    if not result:
        raise HTTPException(status_code=404, detail="Request does not exist.")

    if not result.userID == user.get("userID"):
        raise HTTPException(status_code=403, detail="You do not have access to this request.")

    await db.delete(result)
    await db.commit()


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_request(user: user_dependency, request_request: RequestsRequest, db: db_dependency):

    query = select(models.ai_model).filter(models.ai_model.modelID == request_request.modelID)
    model_raw = await db.execute(query)
    model_exists = model_raw.scalars().first()

    if not model_exists:
        raise HTTPException(status_code=404, detail="Model not found.")
    new_input = models.inputs(input_text=request_request.input_text)

    db.add(new_input)
    await db.flush()

    response_text = f"Models output : {request_request.input_text[::-1]}"

    new_output = models.outputs(output_text = response_text)

    db.add(new_output)
    await db.flush()

    new_request = requests(
        userID = user.get("userID"),
        modelID = request_request.modelID,
        inputID = new_input.inputID,
        outputID = new_output.outputID
    )

    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)
    return new_request