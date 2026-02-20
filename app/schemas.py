from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List

class InsuranceInput(BaseModel):
    age: int
    sex: str
    bmi: float
    children: int
    smoker: str
    region: str


class InsuranceResponse(BaseModel):
    id: str   
    predicted_premium: float
    risk_level: str

    model_config = ConfigDict(from_attributes=True)





class PredictionListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[InsuranceResponse]

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


