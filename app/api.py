# app/api.py

from fastapi import APIRouter, HTTPException, status, Depends
from app import service
from app.schemas import ExtractRequest, ExtractResponse

router = APIRouter()

@router.post(
    "/extract-data",
    response_model=ExtractResponse,
    summary="Extract and validate student document data (KTP, Passport, Ijazah, etc.)",
    status_code=status.HTTP_200_OK,
)
def extract_data(request: ExtractRequest):
    """
    Receives a document URL and document type, and returns structured extracted data.
    """
    try:
        result = service.extract_document_data(
            url=str(request.url),
            doc_type=str(request.doc_type)
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract data: {e}")
