# app/service.py

from app.schemas import ExtractResponse
from app.extractor.preprocessor import (
    get_file_type_from_url, 
    convert_image_url_to_base64_png, 
    convert_pdf_url_to_base64_images, 
    rotate_base64_image
)
from app.extractor.llm_extract import (
    extract_data_from_base64_image,
    prompt_extract_data_from_ktp,
    prompt_extract_data_from_passport,
    prompt_extract_data_from_ijazah,
    ExtractDataFromKTP,
    ExtractDataFromPassport,
    ExtractDataFromIjazah,
)
from typing import Dict

def extract_document_data(url: str, doc_type: str) -> ExtractResponse:

    # Step 1: Choose prompt/schema based on doc_type
    if doc_type == "ktp":
        json_schema = ExtractDataFromKTP
        prompt_extractor = prompt_extract_data_from_ktp
    elif doc_type == "passport":
        json_schema = ExtractDataFromPassport
        prompt_extractor = prompt_extract_data_from_passport
    elif doc_type == "ijazah":
        json_schema = ExtractDataFromIjazah
        prompt_extractor = prompt_extract_data_from_ijazah
    else:
        return ExtractResponse(
            is_document=False, 
            message=f"Unsupported document type: {doc_type}"
        )

    # Step 2: Get File Type
    file_type = get_file_type_from_url(url)
    if file_type not in ('image', 'pdf'):
        return ExtractResponse(is_document=False, message="Unsupported or unknown file type.")
    
    # Step 3: Download/Convert to base64 PNG images
    try:
        if file_type == 'image':
            base64_images = convert_image_url_to_base64_png(url)
        elif file_type == 'pdf':
            base64_images = convert_pdf_url_to_base64_images(url)
        else:
            base64_images = []
    except Exception as e:
        return ExtractResponse(is_document=False, message=f"Could not process file: {e}")
    
    # Step 4: Process each image, try extracting info
    for base64_image in base64_images:
        try:
            extracted_data: Dict = extract_data_from_base64_image(
                base64_image, json_schema, prompt_extractor
            )
        except Exception as e:
            return ExtractResponse(is_document=False, message=f"LLM extraction failed: {e}")

        if extracted_data.get("is_document", False):
            # Try auto-orientation
            orientation = extracted_data.get("orientation", 0)
            max_attempts = 4
            attempts = 0

            while orientation != 0 and attempts < max_attempts:
                base64_image = rotate_base64_image(base64_image, -orientation)
                extracted_data = extract_data_from_base64_image(
                    base64_image, json_schema, prompt_extractor
                )
                orientation = extracted_data.get("orientation", 0)
                attempts += 1

            if orientation == 0:
                return ExtractResponse(**extracted_data)
            else:
                return ExtractResponse(
                    is_document=True,
                    message="Failed to auto-correct document orientation after maximum attempts.",
                    **extracted_data
                )
    # If no document found
    return ExtractResponse(is_document=False, message="Valid document not found in file.")
