from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend import models, database, auth
from pydantic import BaseModel

router = APIRouter()

# Pydantic model for admin login
class AdminLogin(BaseModel):
    username: str
    password: str

# Admin login
@router.post('/admin/login')
async def admin_login(admin_data: AdminLogin, db: Session = Depends(database.get_db)):
    admin_user = db.query(models.User).filter(models.User.username == admin_data.username, models.User.is_admin == True).first()
    if not admin_user or not auth.verify_password(admin_data.password, admin_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Generate an admin JWT token here (optional)
    token = auth.create_access_token({"sub": admin_user.username, "admin": True})
    
    return {"message": "Admin login successful", "token": token}

# Admin route to fetch all users
@router.get('/admin/users')
async def get_all_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    
    return {"message": "All users fetched successfully", "users": users}

# Admin route to delete a user
@router.delete('/admin/user/{user_id}')
async def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}
