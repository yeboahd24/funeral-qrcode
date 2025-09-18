from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from app.database import engine, Base
from app.routers import funeral, admin, qr_codes
from app.models import funeral as funeral_models

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Funeral Program System",
    description="A digital funeral program system with QR code access",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/qr_codes", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(funeral.router, prefix="/api/funeral", tags=["funeral"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(qr_codes.router, prefix="/api/qr", tags=["qr_codes"])

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Funeral Program System</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 40px; }
                .api-links { margin: 20px 0; }
                .api-links a { display: block; margin: 10px 0; padding: 10px; background: #f0f0f0; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Funeral Program System</h1>
                    <p>A digital funeral program system with QR code access</p>
                </div>
                <div class="api-links">
                    <h3>API Documentation</h3>
                    <a href="/docs">Interactive API Documentation (Swagger UI)</a>
                    <a href="/redoc">Alternative API Documentation (ReDoc)</a>
                </div>
                <div class="api-links">
                    <h3>Quick Links</h3>
                    <a href="/api/admin/dashboard">Admin Dashboard</a>
                    <a href="/api/funeral/programs">View All Programs</a>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Funeral Program System is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)