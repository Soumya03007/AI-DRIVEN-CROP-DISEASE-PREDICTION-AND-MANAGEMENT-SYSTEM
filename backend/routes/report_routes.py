from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend import models, database
from backend.auth import get_current_user

router = APIRouter()

# Fetch user reports
@router.get('/reports')
async def fetch_user_reports(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    reports = db.query(models.Report).filter(models.Report.user_id == current_user.id).all()
    
    return {"message": "User reports fetched successfully", "reports": reports}
