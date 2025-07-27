# Funeral Program System

A comprehensive digital funeral program system with QR code access, admin authentication, and PDF generation capabilities.

## Features

### ✅ Completed Features

1. **Admin Authentication System**
   - User registration and login
   - Session-based authentication with JWT tokens
   - Protected admin routes
   - Secure password hashing

2. **Complete Template System**
   - Admin dashboard
   - Login/registration forms
   - Program creation and editing forms
   - Public funeral program display
   - Obituary display
   - Responsive design with print-friendly styles

3. **PDF Generation for Obituaries**
   - Professional PDF layout with ReportLab
   - Includes photos, biography, family details
   - Downloadable from admin interface
   - Public access via QR codes

4. **QR Code Integration**
   - Unique QR codes for each program
   - PNG and SVG format support
   - Direct access to funeral programs

5. **Database Models**
   - Funeral programs with events
   - Obituaries with rich content
   - Admin user management
   - Photo and file upload support

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the application:
```bash
python main.py
```

3. Access the system:
   - Home: http://localhost:8000
   - Admin Registration: http://localhost:8000/api/admin/register
   - Admin Login: http://localhost:8000/api/admin/login
   - API Docs: http://localhost:8000/docs

## Quick Start

1. **Create Admin Account**
   - Visit `/api/admin/register`
   - Fill in username, email, and password
   - Login with your credentials

2. **Create Funeral Program**
   - Access admin dashboard
   - Click "Create New Program"
   - Fill in deceased information and obituary
   - Upload photo (optional)

3. **Generate QR Code**
   - QR code is automatically generated
   - Download from program detail page
   - Print and share with attendees

4. **Generate PDF Obituary**
   - Click "Download PDF" on program detail page
   - Professional PDF with all obituary content
   - Suitable for printing and sharing

## API Endpoints

### Public Access
- `GET /` - Home page
- `GET /api/funeral/program/{qr_code_id}/view` - View funeral program
- `GET /api/funeral/program/{qr_code_id}/obituary/view` - View obituary

### Admin (Authentication Required)
- `GET /api/admin/dashboard` - Admin dashboard
- `POST /api/admin/create` - Create funeral program
- `GET /api/admin/program/{id}` - View program details
- `GET /api/admin/program/{id}/edit` - Edit program
- `GET /api/admin/program/{id}/obituary/pdf` - Download obituary PDF

### Authentication
- `GET /api/admin/login` - Login form
- `POST /api/admin/login` - Process login
- `GET /api/admin/register` - Registration form
- `POST /api/admin/register` - Process registration
- `POST /api/admin/logout` - Logout

## File Structure

```
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── app/
│   ├── __init__.py
│   ├── database.py         # Database configuration
│   ├── models/
│   │   └── funeral.py      # SQLAlchemy models
│   ├── routers/
│   │   ├── admin.py        # Admin routes with authentication
│   │   ├── funeral.py      # Public funeral program routes
│   │   └── qr_codes.py     # QR code generation routes
│   ├── schemas/
│   │   └── funeral.py      # Pydantic schemas
│   └── utils/
│       ├── auth.py         # Authentication utilities
│       ├── pdf_generator.py # PDF generation with ReportLab
│       └── qr_generator.py # QR code generation
├── templates/              # Jinja2 HTML templates
│   ├── base.html          # Base template with styling
│   ├── admin_dashboard.html
│   ├── admin_program_detail.html
│   ├── create_program.html
│   ├── edit_program.html
│   ├── funeral_program.html
│   ├── obituary.html
│   ├── login.html
│   └── register.html
└── static/                # Static files
    ├── uploads/           # Uploaded photos
    ├── qr_codes/          # Generated QR codes
    └── pdfs/              # Generated PDF files
```

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- HTTP-only cookies for session management
- Protected admin routes
- Input validation and sanitization

## Technologies Used

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Authentication**: JWT tokens, bcrypt
- **PDF Generation**: ReportLab
- **QR Codes**: qrcode library
- **Templates**: Jinja2
- **Styling**: Custom CSS with responsive design

## Production Deployment

For production deployment:

1. Set environment variables:
   - `SECRET_KEY`: Strong secret key for JWT
   - `DATABASE_URL`: Production database URL

2. Enable HTTPS and update cookie settings:
   - Set `secure=True` for cookies
   - Configure CORS appropriately

3. Use a production ASGI server:
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

## Support

This system provides a complete digital funeral program solution with modern web technologies and security best practices.