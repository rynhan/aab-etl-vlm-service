# app/schemas.py

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Literal



# Input (request)

class ExtractRequest(BaseModel):
    url: HttpUrl = Field(..., description="The URL to the image or PDF document.")
    doc_type: Literal['ktp', 'passport', 'ijazah'] = Field(
        ...,
        description="Type of document: 'ktp', 'passport', or 'ijazah'."
    )



# Output (response)

class ExtractResponse(BaseModel):
    # These fields cover KTP, Passport, and Ijazah scenarios
    is_document: bool = Field(..., description="Whether the document matches the expected type.")
    orientation: Optional[int] = Field(None, description="Image rotation (degrees).")
    id_number: Optional[str] = Field(None, description="ID/Passport number if available.")
    fullname: Optional[str] = Field(None, description="Full name as extracted.")
    date_of_birth: Optional[str] = Field(None, description="Birthday in YYYY-MM-DD format.")
    place_of_birth: Optional[str] = Field(None, description="Place of birth (city).")
    sex: Optional[str] = Field(None, description="Gender (if available).")
    nationality: Optional[str] = Field(None, description="Nationality code or WNI/WNA for KTP.")
    message: Optional[str] = Field(None, description="Error, warning, or info message.")  # Generic message

    # Optionally, you can add an 'extras' dict if you want extensibility for future document types.
