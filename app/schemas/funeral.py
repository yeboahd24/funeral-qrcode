from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

# Program Event Schemas
class ProgramEventBase(BaseModel):
    time: str
    title: str
    description: Optional[str] = None
    speaker_name: Optional[str] = None
    order_index: int

class ProgramEventCreate(ProgramEventBase):
    pass

class ProgramEventUpdate(BaseModel):
    time: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    speaker_name: Optional[str] = None
    order_index: Optional[int] = None

class ProgramEvent(ProgramEventBase):
    id: int
    funeral_program_id: int
    
    class Config:
        from_attributes = True

# Obituary Schemas
class ObituaryBase(BaseModel):
    biography: str
    family_details: Optional[str] = None
    special_message: Optional[str] = None
    photos: Optional[List[str]] = []
    tributes: Optional[List[Dict[str, Any]]] = []

class ObituaryCreate(ObituaryBase):
    pass

class ObituaryUpdate(BaseModel):
    biography: Optional[str] = None
    family_details: Optional[str] = None
    special_message: Optional[str] = None
    photos: Optional[List[str]] = None
    tributes: Optional[List[Dict[str, Any]]] = None

class Obituary(ObituaryBase):
    id: int
    funeral_program_id: int
    pdf_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Funeral Program Schemas
class FuneralProgramBase(BaseModel):
    deceased_name: str
    date_of_birth: Optional[str] = None
    date_of_death: Optional[str] = None
    funeral_date: str
    funeral_location: str
    deceased_photo_url: Optional[str] = None

class FuneralProgramCreate(FuneralProgramBase):
    program_events: List[ProgramEventCreate] = []
    obituary: Optional[ObituaryCreate] = None

class FuneralProgramUpdate(BaseModel):
    deceased_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    date_of_death: Optional[str] = None
    funeral_date: Optional[str] = None
    funeral_location: Optional[str] = None
    deceased_photo_url: Optional[str] = None
    is_active: Optional[bool] = None

class FuneralProgram(FuneralProgramBase):
    id: int
    qr_code_id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    program_events: List[ProgramEvent] = []
    obituary: Optional[Obituary] = None
    
    class Config:
        from_attributes = True

# QR Code Response Schema
class QRCodeResponse(BaseModel):
    qr_code_id: str
    qr_code_url: str
    access_url: str

# Public Program Display Schema (for QR code access)
class PublicFuneralProgram(BaseModel):
    deceased_name: str
    date_of_birth: Optional[str] = None
    date_of_death: Optional[str] = None
    funeral_date: str
    funeral_location: str
    deceased_photo_url: Optional[str] = None
    program_events: List[ProgramEvent] = []
    obituary: Optional[Obituary] = None
    
    class Config:
        from_attributes = True

# Admin User Schemas
class AdminUserBase(BaseModel):
    username: str
    email: str

class AdminUserCreate(AdminUserBase):
    password: str

class AdminUser(AdminUserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True