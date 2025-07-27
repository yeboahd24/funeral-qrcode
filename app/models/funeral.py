from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class FuneralProgram(Base):
    __tablename__ = "funeral_programs"
    
    id = Column(Integer, primary_key=True, index=True)
    deceased_name = Column(String(255), nullable=False)
    date_of_birth = Column(String(50))
    date_of_death = Column(String(50))
    funeral_date = Column(String(50), nullable=False)
    funeral_location = Column(String(500), nullable=False)
    deceased_photo_url = Column(String(500))
    qr_code_id = Column(String(100), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    program_events = relationship("ProgramEvent", back_populates="funeral_program", cascade="all, delete-orphan")
    obituary = relationship("Obituary", back_populates="funeral_program", uselist=False, cascade="all, delete-orphan")

class ProgramEvent(Base):
    __tablename__ = "program_events"
    
    id = Column(Integer, primary_key=True, index=True)
    funeral_program_id = Column(Integer, ForeignKey("funeral_programs.id"), nullable=False)
    time = Column(String(20), nullable=False)  # e.g., "10:00 AM"
    title = Column(String(255), nullable=False)
    description = Column(Text)
    speaker_name = Column(String(255))
    order_index = Column(Integer, nullable=False)  # For ordering events
    
    # Relationship
    funeral_program = relationship("FuneralProgram", back_populates="program_events")

class Obituary(Base):
    __tablename__ = "obituaries"
    
    id = Column(Integer, primary_key=True, index=True)
    funeral_program_id = Column(Integer, ForeignKey("funeral_programs.id"), nullable=False)
    biography = Column(Text, nullable=False)
    family_details = Column(Text)
    special_message = Column(Text)
    photos = Column(JSON)  # Store list of photo URLs
    tributes = Column(JSON)  # Store list of tribute messages
    pdf_url = Column(String(500))  # URL to generated PDF
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    funeral_program = relationship("FuneralProgram", back_populates="obituary")

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())