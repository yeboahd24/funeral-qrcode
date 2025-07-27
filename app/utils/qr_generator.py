import qrcode
import qrcode.image.svg
from io import BytesIO
import uuid
import os
from pathlib import Path

def generate_qr_code_id() -> str:
    """Generate a unique QR code ID"""
    return str(uuid.uuid4())

def create_qr_code(qr_code_id: str, base_url: str = None) -> str:
    """
    Create a QR code image and save it to static/qr_codes/
    Returns the file path of the generated QR code
    """
    # Get base URL from environment or use default
    if base_url is None:
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
    
    # Create the access URL
    access_url = f"{base_url}/api/funeral/program/{qr_code_id}/view"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(access_url)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the image
    qr_code_filename = f"{qr_code_id}.png"
    qr_code_path = Path("static/qr_codes") / qr_code_filename
    
    # Ensure directory exists
    qr_code_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the image
    img.save(qr_code_path)
    
    return f"/static/qr_codes/{qr_code_filename}"

def create_qr_code_svg(qr_code_id: str, base_url: str = None) -> str:
    """
    Create a QR code SVG and save it to static/qr_codes/
    Returns the file path of the generated QR code SVG
    """
    # Get base URL from environment or use default
    if base_url is None:
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
    
    # Create the access URL
    access_url = f"{base_url}/api/funeral/program/{qr_code_id}/view"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(access_url)
    qr.make(fit=True)
    
    # Create QR code SVG
    factory = qrcode.image.svg.SvgPathImage
    img = qr.make_image(image_factory=factory)
    
    # Save the SVG
    qr_code_filename = f"{qr_code_id}.svg"
    qr_code_path = Path("static/qr_codes") / qr_code_filename
    
    # Ensure directory exists
    qr_code_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the SVG
    with open(qr_code_path, 'wb') as f:
        img.save(f)
    
    return f"/static/qr_codes/{qr_code_filename}"