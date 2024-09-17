import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import load_model
import os

# Dataset directory
dataset_dir = "C:/AI-Crop-Disease-App/ml_model/datasets/train"

# Load models for different crops
models = {
    'apple': load_model("C:/AI-Crop-Disease-App/ml_model/model/apple_model/crop_disease_model_apple.keras"),
    'cherry': load_model("C:/AI-Crop-Disease-App/ml_model/model/cherry_model/crop_disease_model_cherry.keras"),
    'corn': load_model("C:/AI-Crop-Disease-App/ml_model/model/corn_model/crop_disease_model_corn1.keras"),
    'grape': load_model("C:/AI-Crop-Disease-App/ml_model/model/grape_model/crop_disease_model_grape.keras"),
    'tomato': load_model("C:/AI-Crop-Disease-App/ml_model/model/tomato_model/crop_disease_model_tomato.keras")
}

# Define class names for each crop
class_names = {
    'corn': [
        'Corn_(maize)_Cercospora_leaf_spot Gray_leaf_spot',
        'Corn_(maize)Common_rust',
        'Corn_(maize)Northern_Leaf_Blight',
        'Corn_(maize)_healthy'
    ],
    'grape': [
        'Grape_Black_rot', 'Grape_Esca(Black_Measels)',
        'Grape_leaf_blight(Isariopsis_leaf_spot)', 'Grape_healthy'
    ],
    'tomato': [
        'Tomato__Bacterial_spot',
        'Tomato_Early_blight', 'Tomato_healthy', 'Tomato_Late_blight',
        'Tomato_Leaf_Mold', 'Tomato_Septoria_leaf_spot',
        'Tomato_Spider_mites Two-spotted_spider_mite', 'Tomato_Target_Spot',
        'Tomato__Tomato_mosaic_virus', 'Tomato_Tomato_Yellow_Leaf_Curl_Virus'
    ],
    'apple': [
        'Apple_BlackRot', 'Apple_Healthy', 'Apple_Scab',
        'Apple_Cedar_apple_rust'
    ],
    'cherry': [
        'Cherry_(including_sour)_Powdery_mildew',
        'Cherry_(including_sour)_healthy'
    ]
}

# Define disease information for each crop
disease_info = {
    'Corn_(maize)_Cercospora_leaf_spot Gray_leaf_spot': {
        'Preventive Measures': "Practice crop rotation and use resistant varieties. Ensure good field drainage.",
        'Medications': "Apply fungicides like chlorothalonil or azoxystrobin to manage symptoms."
    },
    'Corn_(maize)Common_rust': {
        'Preventive Measures': "Use resistant varieties and practice crop rotation. Avoid planting in the same field year after year.",
        'Medications': "Fungicides such as propiconazole or tebuconazole can help control rust."
    },
    'Corn_(maize)Northern_Leaf_Blight': {
        'Preventive Measures': "Practice crop rotation and remove infected plant debris. Ensure good air circulation.",
        'Medications': "Apply fungicides like mancozeb or pyraclostrobin to control the disease."
    },
    'Corn_(maize)_healthy': {
        'Preventive Measures': "Maintain good field management practices including proper irrigation and pest control.",
        'Medications': "No action needed."
    },
    'Apple_Scab': {
        'Preventive Measures': "Rake and destroy fallen leaves, and prune the tree to promote airflow.",
        'Medications': "Apply fungicides such as captan or mancozeb at regular intervals."
    },
    'Apple_BlackRot': {
        'Preventive Measures': "Remove infected fruit and prune dead or cankered limbs. Avoid injuries to the tree.",
        'Medications': "Fungicides like benomyl or thiophanate-methyl can be used to treat infections."
    },
    'Apple_Cedar_apple_rust': {
        'Preventive Measures': "Remove nearby juniper trees, which host the rust, and ensure proper tree spacing.",
        'Medications': "Use fungicides such as myclobutanil to control the disease."
    },
    'Apple_Healthy': {
        'Preventive Measures': "Maintain regular tree inspections, proper pruning, and good irrigation practices.",
        'Medications': "No action needed."
    },
    'Cherry_(including_sour)_Powdery_mildew': {
        'Preventive Measures': "Ensure good air circulation and avoid overhead watering. Remove and destroy infected plant parts.",
        'Medications': "Apply fungicides such as sulfur or potassium bicarbonate to control the spread."
    },
    'Cherry_(including_sour)_healthy': {
        'Preventive Measures': "Maintain proper orchard management practices including regular inspections and balanced fertilization.",
        'Medications': "No action needed."
    },
    'Grape_Black_rot': {
        'Preventive Measures': "Prune vines to improve airflow and remove diseased plant debris. Rotate crops regularly.",
        'Medications': "Apply fungicides such as mancozeb or captan to control the spread."
    },
    'Grape_Esca(Black_Measels)': {
        'Preventive Measures': "Avoid injuries to vines during pruning and limit water stress.",
        'Medications': "There are no effective chemical treatments for Esca. Manage the disease through good viticultural practices."
    },
    'Grape_leaf_blight(Isariopsis_leaf_spot)': {
        'Preventive Measures': "Improve air circulation by pruning and avoid overwatering. Remove infected leaves.",
        'Medications': "Fungicide applications, such as copper-based products, may help."
    },
    'Grape_healthy': {
        'Preventive Measures': "Maintain regular inspection of plants and ensure proper irrigation practices.",
        'Medications': "No action needed."
    },
    'Tomato_Bacterial_spot': {
        'Preventive Measures': "Use disease-free seeds and resistant varieties. Avoid overhead irrigation and practice crop rotation.",
        'Medications': "Apply copper-based fungicides to control the spread of the disease."
    },
    'Tomato_Early_blight': {
        'Preventive Measures': "Practice crop rotation and use resistant varieties. Remove infected plant debris.",
        'Medications': "Fungicides like mancozeb or chlorothalonil can help manage symptoms."
    },
    'Tomato_Tomato_mosaic_virus': {
        'Preventive Measures': "Use virus-free seeds and practice good sanitation. Remove and destroy infected plants.",
        'Medications': "No chemical treatment available; focus on prevention and control of aphid populations."
    },
    'Tomato_healthy': {
        'Preventive Measures': "Maintain good field management practices, proper irrigation, and pest control.",
        'Medications': "No action needed."
    }
}

# Function to preprocess the image
def preprocess_image(img_path, target_size=(180, 180)):
    """
    Preprocess the image to be used by the model.
    """
    try:
        img = cv.imread(img_path)
        if img is None:
            raise FileNotFoundError(f"Image not found at {img_path}")
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img_resized = cv.resize(img, target_size)
        img_array = np.array([img_resized]) / 255.0  # Normalize the image
        return img_resized, img_array
    except Exception as e:
        raise RuntimeError(f"Error processing image: {e}")

# Prediction function for a given crop type
def predict_disease(crop_type, img_path):
    """
    Predicts the disease for a given crop type using the appropriate model.
    """
    if crop_type not in models:
        print(f"Error: No model available for the crop type '{crop_type}'")
        return {"disease": "Unknown", "solution": "No solution provided"}

    model = models[crop_type]
    class_names_list = class_names[crop_type]

    try:
        # Preprocess the image
        img_resized, img_array = preprocess_image(img_path)

        # Display the image (useful for debugging, can be disabled in production)
        # plt.imshow(img_resized)
        # plt.axis('off')
        # plt.show()

        # Make the prediction
        prediction = model.predict(img_array)
        index = np.argmax(prediction)

        # Get the predicted label
        predicted_label = class_names_list[index]
        print(f'Prediction: {predicted_label}')

        # Fetch and return preventive measures and medications
        if predicted_label in disease_info:
            preventive_measures = disease_info[predicted_label]['Preventive Measures']
            medications = disease_info[predicted_label]['Medications']
            return {
                "disease": predicted_label,
                "solution": {
                    "Preventive Measures": preventive_measures,
                    "Medications": medications
                }
            }
        else:
            return {
                "disease": predicted_label,
                "solution": "No information available for this disease."
            }

    except Exception as e:
        return {"error": str(e)}

# Main logic for integration
if __name__ == '__main__':
    crop_type = input("Enter crop type (corn, grape, tomato, apple, cherry): ").strip().lower()
    img_path = input("Enter the image path: ").strip()

    # Validate the image path
    if not os.path.exists(img_path):
        print(f"Error: Image path '{img_path}' does not exist.")
    else:
        # Run the prediction if a valid crop type and image path are provided
        result = predict_disease(crop_type, img_path)
        print("Prediction Result:", result)
