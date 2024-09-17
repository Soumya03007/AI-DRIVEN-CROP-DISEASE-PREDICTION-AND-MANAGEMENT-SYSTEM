from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone  # Import timezone for UTC

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # Password will be hashed
    registered_on = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # Timezone-aware UTC

    # Relationship with Report
    reports = relationship("Report", back_populates="user")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    crop_type = Column(String, index=True)
    image_path = Column(String)
    predicted_disease = Column(String)
    solution = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # Add timestamp with UTC
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationship with User
    user = relationship("User", back_populates="reports")
