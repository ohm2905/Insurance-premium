from sqlalchemy.orm import Session
from . import models
from .auth import hash_password, verify_password


# ------------------- PREDICTION -------------------

def create_prediction(db: Session, data, premium: float, risk: str, user_id: str):
    new_record = models.InsuranceRecord(
        age=data.age,
        sex=data.sex,
        bmi=data.bmi,
        children=data.children,
        smoker=data.smoker,
        region=data.region,
        predicted_premium=premium,
        risk_level=risk,
        user_id=user_id  
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


def get_prediction_by_id(db: Session, record_id: str, user_id: str):
    return db.query(models.InsuranceRecord).filter(
        models.InsuranceRecord.id == str(record_id),
        models.InsuranceRecord.user_id == user_id  
    ).first()


def delete_prediction(db: Session, record_id: str, user_id: str):
    record = db.query(models.InsuranceRecord).filter(
        models.InsuranceRecord.id == str(record_id),
        models.InsuranceRecord.user_id == user_id  
    ).first()

    if not record:
        return None

    db.delete(record)
    db.commit()
    return record


def get_predictions(
    db: Session,
    user_id: str,
    risk_level: str = None,
    smoker: str = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = None,
    order: str = "asc"
):
   
    query = db.query(models.InsuranceRecord).filter(
        models.InsuranceRecord.user_id == user_id
    )

    if risk_level:
        query = query.filter(models.InsuranceRecord.risk_level == risk_level)

    if smoker:
        query = query.filter(models.InsuranceRecord.smoker == smoker)

    total = query.count()

 
    if sort_by and hasattr(models.InsuranceRecord, sort_by):
        column = getattr(models.InsuranceRecord, sort_by)
        if order == "desc":
            column = column.desc()
        query = query.order_by(column)

    records = query.offset(skip).limit(limit).all()

    return total, records


# ------------------- USER -------------------

def create_user(db: Session, username: str, password: str):
    hashed_pw = hash_password(password)

    new_user = models.User(
        username=username,
        hashed_password=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(
        models.User.username == username
    ).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
