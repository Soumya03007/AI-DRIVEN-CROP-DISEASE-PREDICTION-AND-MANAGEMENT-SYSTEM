from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend import models, database, auth
from pydantic import BaseModel

router = APIRouter()

# Pydantic models for request bodies
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# User registration
@router.post('/register')
async def register_user(user_data: UserRegister, db: Session = Depends(database.get_db)):
    hashed_password = auth.get_password_hash(user_data.password)
    new_user = models.User(username=user_data.username, password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully"}

# User login
@router.post('/login')
async def login_user(user_data: UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if not user or not auth.verify_password(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Generate a JWT token here (optional)
    token = auth.create_access_token({"sub": user.username})
    
    return {"message": "Login successful", "token": token}
