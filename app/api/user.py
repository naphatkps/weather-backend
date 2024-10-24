from fastapi import Depends
from fastapi.params import Annotated
from pydantic import BaseModel, EmailStr
from app.models.user import User
from app.database import  SessionLocal
from sqlalchemy.orm import Session
from fastapi import APIRouter

router = APIRouter()

class UserBase(BaseModel):
    email: EmailStr

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post('/users/')
async def create_user(user: UserBase, db: Session = Depends(get_db)):
    db_user = User(email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get('/users/')
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()