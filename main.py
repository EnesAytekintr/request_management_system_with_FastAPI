from fastapi import FastAPI
from routers import auth, request, user, model

app = FastAPI()


app.include_router(auth.router)
app.include_router(request.router)
app.include_router(model.router)
app.include_router(user.router)