from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.funeral import FuneralProgram, ProgramEvent, Obituary
from app.schemas.funeral import PublicFuneralProgram, FuneralProgram as FuneralProgramSchema

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/programs", response_model=List[FuneralProgramSchema])
async def get_all_programs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all funeral programs (for admin use)"""
    programs = db.query(FuneralProgram).filter(FuneralProgram.is_active == True).offset(skip).limit(limit).all()
    return programs

@router.get("/program/{qr_code_id}", response_model=PublicFuneralProgram)
async def get_program_by_qr(qr_code_id: str, db: Session = Depends(get_db)):
    """Get funeral program by QR code ID (public access)"""
    program = db.query(FuneralProgram).filter(
        FuneralProgram.qr_code_id == qr_code_id,
        FuneralProgram.is_active == True
    ).first()
    
    if not program:
        raise HTTPException(status_code=404, detail="Funeral program not found")
    
    return program

@router.get("/program/{qr_code_id}/view", response_class=HTMLResponse)
async def view_program(request: Request, qr_code_id: str, db: Session = Depends(get_db)):
    """View funeral program in HTML format"""
    program = db.query(FuneralProgram).filter(
        FuneralProgram.qr_code_id == qr_code_id,
        FuneralProgram.is_active == True
    ).first()
    
    if not program:
        raise HTTPException(status_code=404, detail="Funeral program not found")
    
    # Sort events by order_index
    sorted_events = sorted(program.program_events, key=lambda x: x.order_index)
    
    return templates.TemplateResponse("funeral_program.html", {
        "request": request,
        "program": program,
        "events": sorted_events,
        "obituary": program.obituary
    })

@router.get("/program/{qr_code_id}/obituary")
async def get_obituary(qr_code_id: str, db: Session = Depends(get_db)):
    """Get obituary for a funeral program"""
    program = db.query(FuneralProgram).filter(
        FuneralProgram.qr_code_id == qr_code_id,
        FuneralProgram.is_active == True
    ).first()
    
    if not program:
        raise HTTPException(status_code=404, detail="Funeral program not found")
    
    if not program.obituary:
        raise HTTPException(status_code=404, detail="Obituary not found for this program")
    
    return program.obituary

@router.get("/program/{qr_code_id}/obituary/view", response_class=HTMLResponse)
async def view_obituary(request: Request, qr_code_id: str, db: Session = Depends(get_db)):
    """View obituary in HTML format"""
    program = db.query(FuneralProgram).filter(
        FuneralProgram.qr_code_id == qr_code_id,
        FuneralProgram.is_active == True
    ).first()
    
    if not program:
        raise HTTPException(status_code=404, detail="Funeral program not found")
    
    if not program.obituary:
        raise HTTPException(status_code=404, detail="Obituary not found for this program")
    
    return templates.TemplateResponse("obituary.html", {
        "request": request,
        "program": program,
        "obituary": program.obituary
    })