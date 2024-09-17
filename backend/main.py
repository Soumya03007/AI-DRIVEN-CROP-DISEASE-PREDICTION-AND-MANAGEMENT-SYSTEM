import os
import logging
import uuid
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from models import User, Report, Base  # Add Base
from database import engine, get_db  # Import engine to bind metadata
from auth import create_user, authenticate_user, get_user_by_email
from utils.ml_integration import predict_disease
from datetime import datetime, timezone

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Ensure temp directory exists
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Create the database tables if they don't exist
Base.metadata.create_all(bind=engine)  # This line creates the tables

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production for security
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Crop Disease App"}

@app.post("/register")
def register(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, email, password)

@app.post("/login")
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    return authenticate_user(db, email, password)

@app.post("/upload-image/")
async def upload_image(crop_type: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    logging.info("Image upload initiated")
    logging.info(f"Received crop type: '{crop_type}'")

    # Define valid crop types
    valid_crop_types = ['corn', 'grape', 'tomato', 'apple', 'cherry']
    
    # Validate crop type
    if crop_type not in valid_crop_types:
        logging.error(f"Invalid crop type provided: '{crop_type}'")
        raise HTTPException(status_code=400, detail="Invalid crop type provided")
    
    # Generate a unique filename to avoid overwriting
    filename = f"{uuid.uuid4()}.jpg"  # Adjust extension based on actual file type
    file_location = os.path.join(TEMP_DIR, filename)

    # Save the uploaded file temporarily
    try:
        with open(file_location, "wb") as buffer:
            buffer.write(await file.read())
        logging.info(f"Image saved to {file_location}")
    except Exception as e:
        logging.error(f"Failed to save image: {e}")
        raise HTTPException(status_code=500, detail="Failed to save image")

    # Call the ML model to predict the disease
    try:
        logging.info("Starting prediction with the ML model...")
        result = predict_disease(crop_type, file_location)
        logging.info(f"Prediction complete: {result}")

        # Create and save the report
        report = Report(
            crop_type=crop_type,
            image_path=file_location,
            predicted_disease=result.get("disease", "Unknown"),
            solution=result.get("solution", {}).get("Preventive Measures", "No preventive measures provided"),
            timestamp=datetime.now(timezone.utc)  # Use timezone-aware datetime
        )
        db.add(report)
        db.commit()
        db.refresh(report)
    except Exception as e:
        logging.error(f"Image processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image processing failed: {e}")
    finally:
        # Clean up the temp file
        if os.path.exists(file_location):
            os.remove(file_location)
            logging.info(f"Temporary image file {file_location} removed")

    return {"message": "Image processed successfully", "result": result, "report_id": report.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
