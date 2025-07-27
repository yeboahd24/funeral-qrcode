from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
from pathlib import Path
from datetime import timedelta

from app.database import get_db
from app.models.funeral import FuneralProgram, ProgramEvent, Obituary, AdminUser
from app.schemas.funeral import (
    FuneralProgramCreate, FuneralProgramUpdate, 
    ProgramEventCreate, ObituaryCreate, AdminUserCreate
)
from app.utils.qr_generator import generate_qr_code_id, create_qr_code
from app.utils.auth import (
    get_password_hash, authenticate_user, create_access_token, 
    require_admin_user, get_current_user_optional, ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.utils.pdf_generator import create_obituary_pdf, cleanup_temp_images

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Authentication routes
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request, error: str = None):
    """Show admin login form"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error
    })

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process admin login"""
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password"
        })
    
    if not user.is_active:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Account is inactive"
        })
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Redirect to dashboard with token in cookie
    response = RedirectResponse(url="/api/admin/dashboard", status_code=303)
    response.set_cookie(
        key="session_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=False  # Set to True in production with HTTPS
    )
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request, error: str = None, success: str = None):
    """Show admin registration form"""
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": error,
        "success": success
    })

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process admin registration"""
    # Validation
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Passwords do not match"
        })
    
    if len(password) < 6:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Password must be at least 6 characters long"
        })
    
    # Check if username or email already exists
    existing_user = db.query(AdminUser).filter(
        (AdminUser.username == username) | (AdminUser.email == email)
    ).first()
    
    if existing_user:
        error_msg = "Username already exists" if existing_user.username == username else "Email already exists"
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": error_msg
        })
    
    # Create new admin user
    hashed_password = get_password_hash(password)
    new_user = AdminUser(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )
    
    db.add(new_user)
    db.commit()
    
    return templates.TemplateResponse("register.html", {
        "request": request,
        "success": "Account created successfully! You can now login."
    })

@router.post("/logout")
async def logout():
    """Logout admin user"""
    response = RedirectResponse(url="/api/admin/login", status_code=303)
    response.delete_cookie(key="session_token")
    return response

def get_current_admin_user(
    session_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Dependency to get current admin user with proper error handling"""
    return require_admin_user(credentials=None, session_token=session_token, db=db)

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Admin dashboard showing all funeral programs"""
    programs = db.query(FuneralProgram).order_by(FuneralProgram.created_at.desc()).all()
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "programs": programs,
        "current_user": current_user
    })

@router.get("/create", response_class=HTMLResponse)
async def create_program_form(
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Show form to create new funeral program"""
    return templates.TemplateResponse("create_program.html", {
        "request": request,
        "current_user": current_user
    })

@router.post("/create")
async def create_funeral_program(
    request: Request,
    deceased_name: str = Form(...),
    date_of_birth: str = Form(""),
    date_of_death: str = Form(""),
    funeral_date: str = Form(...),
    funeral_location: str = Form(...),
    biography: str = Form(...),
    family_details: str = Form(""),
    special_message: str = Form(""),
    deceased_photo: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Create a new funeral program"""
    try:
        # Handle photo upload
        deceased_photo_url = None
        if deceased_photo and deceased_photo.filename:
            # Create uploads directory if it doesn't exist
            upload_dir = Path("static/uploads")
            upload_dir.mkdir(exist_ok=True)
            
            # Save uploaded file
            file_extension = deceased_photo.filename.split(".")[-1]
            filename = f"{deceased_name.replace(' ', '_')}_{generate_qr_code_id()[:8]}.{file_extension}"
            file_path = upload_dir / filename
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(deceased_photo.file, buffer)
            
            deceased_photo_url = f"/static/uploads/{filename}"
        
        # Generate unique QR code ID
        qr_code_id = generate_qr_code_id()
        
        # Create funeral program
        program = FuneralProgram(
            deceased_name=deceased_name,
            date_of_birth=date_of_birth if date_of_birth else None,
            date_of_death=date_of_death if date_of_death else None,
            funeral_date=funeral_date,
            funeral_location=funeral_location,
            deceased_photo_url=deceased_photo_url,
            qr_code_id=qr_code_id
        )
        
        db.add(program)
        db.flush()  # Get the ID
        
        # Create obituary
        obituary = Obituary(
            funeral_program_id=program.id,
            biography=biography,
            family_details=family_details if family_details else None,
            special_message=special_message if special_message else None,
            photos=[deceased_photo_url] if deceased_photo_url else [],
            tributes=[]
        )
        
        db.add(obituary)
        db.commit()
        
        # Generate QR code
        create_qr_code(qr_code_id)
        
        return RedirectResponse(url=f"/api/admin/program/{program.id}", status_code=303)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating program: {str(e)}")

@router.get("/program/{program_id}", response_class=HTMLResponse)
async def view_program_admin(
    request: Request, 
    program_id: int, 
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """View funeral program in admin interface"""
    program = db.query(FuneralProgram).filter(FuneralProgram.id == program_id).first()
    
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    # Sort events by order_index
    sorted_events = sorted(program.program_events, key=lambda x: x.order_index)
    
    return templates.TemplateResponse("admin_program_detail.html", {
        "request": request,
        "program": program,
        "events": sorted_events,
        "obituary": program.obituary
    })

@router.get("/program/{program_id}/edit", response_class=HTMLResponse)
async def edit_program_form(
    request: Request, 
    program_id: int, 
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Show form to edit funeral program"""
    program = db.query(FuneralProgram).filter(FuneralProgram.id == program_id).first()
    
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    # Sort events by order_index
    sorted_events = sorted(program.program_events, key=lambda x: x.order_index)
    
    return templates.TemplateResponse("edit_program.html", {
        "request": request,
        "program": program,
        "events": sorted_events,
        "obituary": program.obituary
    })

@router.post("/program/{program_id}/add-event")
async def add_program_event(
    program_id: int,
    time: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    speaker_name: str = Form(""),
    db: Session = Depends(get_db)
):
    """Add an event to a funeral program"""
    program = db.query(FuneralProgram).filter(FuneralProgram.id == program_id).first()
    
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    # Get the next order index
    max_order = db.query(ProgramEvent).filter(
        ProgramEvent.funeral_program_id == program_id
    ).count()
    
    event = ProgramEvent(
        funeral_program_id=program_id,
        time=time,
        title=title,
        description=description if description else None,
        speaker_name=speaker_name if speaker_name else None,
        order_index=max_order + 1
    )
    
    db.add(event)
    db.commit()
    
    return RedirectResponse(url=f"/api/admin/program/{program_id}/edit", status_code=303)

@router.post("/program/{program_id}/delete")
async def delete_program(program_id: int, db: Session = Depends(get_db)):
    """Delete a funeral program"""
    program = db.query(FuneralProgram).filter(FuneralProgram.id == program_id).first()
    
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    # Delete associated files
    if program.deceased_photo_url:
        photo_path = Path(f"static{program.deceased_photo_url}")
        if photo_path.exists():
            photo_path.unlink()
    
    # Delete QR code file
    qr_path = Path(f"static/qr_codes/{program.qr_code_id}.png")
    if qr_path.exists():
        qr_path.unlink()
    
    db.delete(program)
    db.commit()
    
    return RedirectResponse(url="/api/admin/dashboard", status_code=303)

# PDF Generation routes
@router.get("/program/{program_id}/obituary/pdf")
async def generate_obituary_pdf(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Generate and download obituary PDF"""
    program = db.query(FuneralProgram).filter(FuneralProgram.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Funeral program not found")
    
    if not program.obituary:
        raise HTTPException(status_code=404, detail="No obituary found for this program")
    
    try:
        # Generate PDF
        pdf_url = create_obituary_pdf(program, program.obituary)
        
        # Update obituary with PDF URL
        program.obituary.pdf_url = pdf_url
        db.commit()
        
        # Clean up temporary images
        cleanup_temp_images()
        
        # Return file for download
        pdf_path = Path(f".{pdf_url}")
        if not pdf_path.exists():
            raise HTTPException(status_code=500, detail="PDF generation failed")
        
        safe_name = "".join(c for c in program.deceased_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"{safe_name}_obituary.pdf"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.get("/program/{program_id}/obituary/pdf/view")
async def view_obituary_pdf(
    program_id: int,
    db: Session = Depends(get_db)
):
    """View obituary PDF in browser (public access via QR code)"""
    program = db.query(FuneralProgram).filter(FuneralProgram.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Funeral program not found")
    
    if not program.obituary or not program.obituary.pdf_url:
        raise HTTPException(status_code=404, detail="No PDF available for this obituary")
    
    pdf_path = Path(f".{program.obituary.pdf_url}")
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{program.deceased_name.replace(' ', '_')}_obituary.pdf"
    )