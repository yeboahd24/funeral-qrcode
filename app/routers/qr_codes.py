from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.database import get_db
from app.models.funeral import FuneralProgram
from app.utils.qr_generator import create_qr_code, create_qr_code_svg
from app.schemas.funeral import QRCodeResponse

router = APIRouter()

@router.get("/generate/{program_id}", response_model=QRCodeResponse)
async def generate_qr_code(program_id: int, db: Session = Depends(get_db)):
    """Generate QR code for a funeral program"""
    program = db.query(FuneralProgram).filter(FuneralProgram.id == program_id).first()
    
    if not program:
        raise HTTPException(status_code=404, detail="Funeral program not found")
    
    # Generate QR code image
    qr_code_url = create_qr_code(program.qr_code_id)
    access_url = f"/api/funeral/program/{program.qr_code_id}/view"
    
    return QRCodeResponse(
        qr_code_id=program.qr_code_id,
        qr_code_url=qr_code_url,
        access_url=access_url
    )

@router.get("/download/{qr_code_id}")
async def download_qr_code(qr_code_id: str, format: str = "png", db: Session = Depends(get_db)):
    """Download QR code image"""
    program = db.query(FuneralProgram).filter(FuneralProgram.qr_code_id == qr_code_id).first()
    
    if not program:
        raise HTTPException(status_code=404, detail="Funeral program not found")
    
    if format.lower() == "svg":
        qr_code_path = create_qr_code_svg(qr_code_id)
        file_path = Path(f".{qr_code_path}")  # qr_code_path already includes /static/
        media_type = "image/svg+xml"
    else:
        qr_code_path = create_qr_code(qr_code_id)
        file_path = Path(f".{qr_code_path}")  # qr_code_path already includes /static/
        media_type = "image/png"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="QR code file not found")
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=f"{program.deceased_name.replace(' ', '_')}_qr_code.{format.lower()}"
    )