from fastapi import FastAPI
from .database import engine, Base
from .routers import prediction
from . import models

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(prediction.router)

@app.get("/")
def read_root():
    return {"message": "Insurance Premium Prediction API is running"}
