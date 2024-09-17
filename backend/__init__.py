from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routes import auth_routes, image_routes, report_routes, admin_routes

# Initialize FastAPI application
app = FastAPI()

# Enable CORS for frontend communication
origins = [
    "http://localhost:3000",  # Allow frontend on this port
    "http://localhost:8000",  # Backend or other services
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the database tables based on SQLAlchemy models
Base.metadata.create_all(bind=engine)

# Register routes with the FastAPI app
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(image_routes.router, prefix="/images", tags=["Images"])
app.include_router(report_routes.router, prefix="/reports", tags=["Reports"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])

# Root route to check if the app is running
@app.get("/")
def read_root():
    return {"message": "Welcome to the Crop Disease Prediction System!"}
