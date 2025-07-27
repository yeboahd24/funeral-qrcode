from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from io import BytesIO
import os
from pathlib import Path
from typing import Optional
import requests
from PIL import Image as PILImage

def create_obituary_pdf(program, obituary, output_path: str = None) -> str:
    """
    Generate a PDF obituary for a funeral program
    Returns the file path of the generated PDF
    """
    if not output_path:
        # Create PDF filename based on deceased name and program ID
        safe_name = "".join(c for c in program.deceased_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        pdf_filename = f"{safe_name}_obituary_{program.id}.pdf"
        output_path = Path("static/pdfs") / pdf_filename
    
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2c3e50')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#7f8c8d')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#2c3e50')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        leading=18
    )
    
    center_style = ParagraphStyle(
        'CustomCenter',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_CENTER,
        leading=18
    )
    
    # Build story (content)
    story = []
    
    # Title
    story.append(Paragraph(program.deceased_name, title_style))
    
    # Dates
    if program.date_of_birth and program.date_of_death:
        dates_text = f"{program.date_of_birth} - {program.date_of_death}"
        story.append(Paragraph(dates_text, subtitle_style))
    
    story.append(Spacer(1, 20))
    
    # Photo (if available)
    if program.deceased_photo_url:
        try:
            # Download and process image
            photo_path = _process_image_for_pdf(program.deceased_photo_url)
            if photo_path:
                img = Image(photo_path, width=2*inch, height=2*inch)
                img.hAlign = 'CENTER'
                story.append(img)
                story.append(Spacer(1, 20))
        except Exception as e:
            print(f"Error processing image: {e}")
    
    # Biography
    if obituary.biography:
        story.append(Paragraph("Biography", heading_style))
        # Split biography into paragraphs
        bio_paragraphs = obituary.biography.split('\n')
        for para in bio_paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
        story.append(Spacer(1, 15))
    
    # Family Details
    if obituary.family_details:
        story.append(Paragraph("Family", heading_style))
        family_paragraphs = obituary.family_details.split('\n')
        for para in family_paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
        story.append(Spacer(1, 15))
    
    # Special Message
    if obituary.special_message:
        story.append(Paragraph("Special Message", heading_style))
        message_paragraphs = obituary.special_message.split('\n')
        for para in message_paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
        story.append(Spacer(1, 15))
    
    # Funeral Service Details
    story.append(Paragraph("Funeral Service", heading_style))
    story.append(Paragraph(f"<b>Date & Time:</b> {program.funeral_date}", body_style))
    story.append(Paragraph(f"<b>Location:</b> {program.funeral_location}", body_style))
    story.append(Spacer(1, 20))
    
    # Tributes (if any)
    if obituary.tributes and len(obituary.tributes) > 0:
        story.append(Paragraph("Tributes & Messages", heading_style))
        for tribute in obituary.tributes[:5]:  # Limit to first 5 tributes
            if isinstance(tribute, dict) and 'message' in tribute and 'author' in tribute:
                story.append(Paragraph(f'"{tribute["message"]}"', body_style))
                story.append(Paragraph(f"- {tribute['author']}", center_style))
                story.append(Spacer(1, 10))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_text = '"In the hearts of those who loved you, you will always be there."'
    story.append(Paragraph(footer_text, center_style))
    
    # Build PDF
    doc.build(story)
    
    # Return relative path for URL
    return f"/static/pdfs/{output_path.name}"

def _process_image_for_pdf(image_url: str) -> Optional[str]:
    """
    Download and process image for PDF inclusion
    Returns local file path or None if processing fails
    """
    try:
        # If it's a local file path, convert to full path
        if image_url.startswith('/static/'):
            local_path = Path(f".{image_url}")
            if local_path.exists():
                return str(local_path)
        
        # If it's a URL, download it
        if image_url.startswith('http'):
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Save temporary image
            temp_dir = Path("static/temp")
            temp_dir.mkdir(exist_ok=True)
            
            # Determine file extension
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            else:
                ext = '.jpg'  # Default
            
            temp_path = temp_dir / f"temp_image_{hash(image_url)}{ext}"
            
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            
            # Process image to ensure it's in correct format
            with PILImage.open(temp_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large
                max_size = (400, 400)
                img.thumbnail(max_size, PILImage.Resampling.LANCZOS)
                
                # Save processed image
                processed_path = temp_dir / f"processed_{temp_path.name}"
                img.save(processed_path, 'JPEG', quality=85)
                
                return str(processed_path)
    
    except Exception as e:
        print(f"Error processing image {image_url}: {e}")
        return None

def cleanup_temp_images():
    """Clean up temporary images"""
    temp_dir = Path("static/temp")
    if temp_dir.exists():
        for file in temp_dir.glob("temp_*"):
            try:
                file.unlink()
            except Exception:
                pass
        for file in temp_dir.glob("processed_*"):
            try:
                file.unlink()
            except Exception:
                pass