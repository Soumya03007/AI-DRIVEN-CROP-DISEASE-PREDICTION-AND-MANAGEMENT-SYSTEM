from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import shutil
import os
from utils.ml_integration import load_model, predict_image

router = APIRouter()

# Dictionary to store the paths to the pre-trained models
MODEL_PATHS = {
    "apple": "C:/AI-Crop-Disease-App/ml_model/model/apple_model/crop_disease_model_apple.keras",
    "corn": "C:/AI-Crop-Disease-App/ml_model/model/corn_model/crop_disease_model_corn1.keras",
    "cherry": "C:/AI-Crop-Disease-App/ml_model/model/cherry_model/crop_disease_model_cherry.keras",
    "grape": "C:/AI-Crop-Disease-App/ml_model/model/grape_model/crop_disease_model_grape.keras",
    "tomato": "C:/AI-Crop-Disease-App/ml_model/model/tomato_model/crop_disease_model_tomato.keras"
}

# Load models only once during startup
loaded_models = {}

def get_model(crop_type):
    if crop_type not in loaded_models:
        model_path = MODEL_PATHS.get(crop_type)
        if not model_path:
            raise HTTPException(status_code=400, detail="Invalid crop type")
        try:
            loaded_models[crop_type] = load_model(model_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")
    return loaded_models[crop_type]

# Ensure the temporary directory exists
os.makedirs("temp_images", exist_ok=True)

@router.post("/upload-image/")
async def upload_image(cropType: str = Form(...), image: UploadFile = File(...)):
    # Check if cropType is valid
    if cropType not in MODEL_PATHS:
        raise HTTPException(status_code=400, detail="Invalid crop type selected")

    # Save uploaded file temporarily
    image_path = f"temp_images/{image.filename}"
    try:
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Load the appropriate model for the crop type
        model = get_model(cropType)

        # Run prediction on the uploaded image
        predicted_disease, solution = predict_image(model, image_path)

    except Exception as e:
        if os.path.exists(image_path):
            os.remove(image_path)  # Cleanup if something goes wrong
        raise HTTPException(status_code=500, detail=f"Error processing the image: {str(e)}")

    # Remove the temporary file after processing
    if os.path.exists(image_path):
        os.remove(image_path)

    return {
        "predicted_disease": predicted_disease,
        "solution": solution
    }
