# app/extractor/preprocessor.py

import mimetypes
import requests
import base64
import io
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_bytes

def get_file_type_from_url(url: str) -> str:
    mime_type, _ = mimetypes.guess_type(url)
    if mime_type is None:
        return 'unknown'
    if mime_type == 'application/pdf':
        return 'pdf'
    if mime_type in ['image/jpeg', 'image/png', 'image/jpg']:
        return 'image'
    return 'unknown'

def convert_image_url_to_base64_png(image_url):
    # Download an image from a URL, upscale if any side < 800, convert to PNG, and return as a base64 string.
    response = requests.get(image_url)
    response.raise_for_status()
    img = Image.open(io.BytesIO(response.content)).convert('RGB')
    width, height = img.size
    if width < 800 or height < 800:
        new_size = (int(width * 2), int(height * 2))
        img = img.resize(new_size, Image.LANCZOS)
    enhanced_img = ImageEnhance.Contrast(img).enhance(1.5) # Increase contrast
    enhanced_img = enhanced_img.filter(ImageFilter.SHARPEN) # Sharpen
    buf = io.BytesIO()
    enhanced_img.save(buf, format='PNG')
    base64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    return [base64_str]

def convert_pdf_url_to_base64_images(pdf_url):
    # Step 1: Download PDF
    response = requests.get(pdf_url)
    response.raise_for_status() # Raise exception if download failed
    # Step 2: Convert PDF to images (list of PIL images, one per page)
    images = convert_from_bytes(response.content)
    base64_images = []
    # Step 3: Encode each image to base64 with preprocessing
    for img in images:
        width, height = img.size
        if width < 800 or height < 800: # Resize if any side < 800
            new_size = (int(width * 2), int(height * 2))
            img = img.resize(new_size, Image.LANCZOS)
        img = ImageEnhance.Contrast(img).enhance(1.5) # Increase contrast
        img = img.filter(ImageFilter.SHARPEN) # Sharpen
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        base64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
        base64_images.append(base64_str)
    return base64_images

def rotate_base64_image(base64_str, angle):
    img_bytes = base64.b64decode(base64_str)
    img = Image.open(io.BytesIO(img_bytes))
    rotated = img.rotate(-angle, expand=True)  # PIL rotates counter-clockwise
    output = io.BytesIO()
    rotated.save(output, format="PNG")
    return base64.b64encode(output.getvalue()).decode("utf-8")