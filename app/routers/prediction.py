from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import joblib
import pandas as pd
import os
from ..auth import create_access_token
from ..auth import get_current_user
from ..database import get_db
from .. import schemas, crud
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

router = APIRouter(prefix="", tags=["Predictions"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "..", "insurance_model.pkl")
model = joblib.load(MODEL_PATH)





@router.post("/predict", response_model=schemas.InsuranceResponse)
def predict(
    data: schemas.InsuranceInput,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    input_df = pd.DataFrame([data.model_dump()])
    prediction = model.predict(input_df)

    premium = round(float(prediction[0]), 2)

    if premium < 10000:
        risk = "Low"
    elif premium < 20000:
        risk = "Medium"
    else:
        risk = "High"

    return crud.create_prediction(
        db, data, premium, risk, current_user.id
    )



@router.get("/predictions", response_model=schemas.PredictionListResponse)
def read_predictions(
    risk_level: Optional[str] = Query(None),
    smoker: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    sort_by: Optional[str] = Query("created_at"),
    order: Optional[str] = Query("desc"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    total, records = crud.get_predictions(
    db=db,
    user_id=current_user.id, 
    risk_level=risk_level,
    smoker=smoker,
    skip=skip,
    limit=limit,
    sort_by=sort_by,
    order=order
)


    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": records
    }


@router.get("/prediction/{record_id}", response_model=schemas.InsuranceResponse)
def get_prediction(record_id: str, db: Session = Depends(get_db),current_user = Depends(get_current_user)):

    record = crud.get_prediction_by_id(db, record_id,current_user.id)

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    return record





@router.delete("/prediction/{record_id}")
def delete_prediction(record_id: str, db: Session = Depends(get_db),current_user = Depends(get_current_user)):

    record = crud.delete_prediction(db, record_id,current_user.id)

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    return {"message": "Record deleted successfully"}


@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = crud.get_user_by_username(db, user.username)

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = crud.create_user(db, user.username, user.password)

    return new_user



@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = crud.authenticate_user(
        db,
        form_data.username,
        form_data.password
    )

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": db_user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


