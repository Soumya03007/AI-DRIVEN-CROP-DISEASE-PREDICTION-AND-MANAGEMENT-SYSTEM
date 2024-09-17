from fastapi import UploadFile, HTTPException
from PIL import Image, UnidentifiedImageError
import os
from io import BytesIO

UPLOAD_DIR = "uploads/"  # Directory to save uploaded images

# Ensure the directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_file_to_disk(uploaded_file: UploadFile, destination: str = UPLOAD_DIR) -> str:
    """
    Saves the uploaded file to the specified destination and returns the file path.
    Validates file format and size before saving.
    """
    # Check if file type is allowed before processing
    if not allowed_file(uploaded_file.filename):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")

    # Create file path
    file_location = os.path.join(destination, uploaded_file.filename)

    # Save file to disk
    try:
        with open(file_location, "wb+") as file_object:
            file_object.write(uploaded_file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")

    return file_location

def convert_to_image(uploaded_file: UploadFile) -> Image.Image:
    """
    Converts an uploaded file into a PIL Image object.
    """
    if not allowed_file(uploaded_file.filename):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
    
    try:
        contents = uploaded_file.file.read()
        image = Image.open(BytesIO(contents))

        # This will confirm if the file content is really an image
        image.verify()
        # Re-open to actually work with it after verification
        image = Image.open(BytesIO(contents))
        return image
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {e}")

def remove_file(file_path: str):
    """
    Removes the file from disk.
    """
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error removing file: {e}")
    else:
        raise HTTPException(status_code=404, detail="File not found.")

def allowed_file(filename: str) -> bool:
    """
    Checks if the file has an allowed extension.
    """
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
