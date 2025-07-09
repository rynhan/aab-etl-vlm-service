# app/extractor/llm_extract.py

from typing_extensions import Annotated, TypedDict
from langchain_openai import ChatOpenAI

# ----------------- TypedDict schemas -----------------

class ExtractDataFromPassport(TypedDict):
    """Extract data from a passport document picture."""
    is_document: Annotated[bool, ..., "Whether the document is a passport or not"]
    orientation: Annotated[int, ..., "The orientation of the given image. Either [0, 90, 180, 270]"]
    id_number: Annotated[str, ..., "The passport ID number"]
    fullname: Annotated[str, ..., "The full name of the person in UPPERCASE"]
    date_of_birth: Annotated[str, ..., "The date of birth of the person in YYYY-MM-DD. ISO 8601"]
    place_of_birth: Annotated[str, ..., "The place of birth (CITY) of the person in UPPERCASE"]
    sex: Annotated[str, ..., "The gender of the person, either \"M\" or \"F\""]
    nationality: Annotated[str, ..., "The nationality of the person. ISO 3166-1 Alpha-2"]

class ExtractDataFromKTP(TypedDict):
    """Extract data from a passport document picture."""
    is_document: Annotated[bool, ..., "Whether the document is a KTP (Indonesian ID card) or not"]
    orientation: Annotated[int, ..., "Give me the orientation of the given image in clockwise. Either [0, 90, 180, 270]. Remember, KTP in 0 degree rotation, the position of head photo is always in the right side of the card. If the photo is in the bottom, it is 90 degree rotated. If the photo is on the left, it is 180 degree rotated. If the photo is on the top, it is 270 degree rotated. Use this as a reference to determine the orientation of the image."]
    id_number: Annotated[str, ..., "The KTP ID number (NIK) conisisting of 16 digits."]
    fullname: Annotated[str, ..., "The full name of the person in UPPERCASE"]
    date_of_birth: Annotated[str, ..., "The date of birth of the person in YYYY-MM-DD. ISO 8601"]
    place_of_birth: Annotated[str, ..., "The place of birth (CITY) of the person in UPPERCASE"]
    sex: Annotated[str, ..., "The gender of the person, either \"M\" or \"F\""]
    nationality: Annotated[str, ..., "The nationality of the person, either \"WNI\" or \"WNA\""]

class ExtractDataFromIjazah(TypedDict):
    """Extract data from an High School Certificate document picture."""
    is_document: Annotated[bool, ..., "Whether the document is an Ijazah or not"]
    orientation: Annotated[int, ..., "Give me the orientation of the given image in clockwise. Either [0, 90, 180, 270]."]
    fullname: Annotated[str, ..., "The fullname of the person in UPPERCASE"]
    date_of_birth: Annotated[str, ..., "The date of birth of the person in YYYY-MM-DD. ISO 8601"]
    place_of_birth: Annotated[str, ..., "The place of birth (CITY) of the person in UPPERCASE"]

# ----------------- Prompt templates ------------------ 

prompt_extract_data_from_ktp = """You are a helpful assistant that extracts information from images of documents.
You will be given an image of a KTP, and your task is to extract the relevant information based on the document type provided.
Your goal is to analyze the image first, give a brief summary what you think especially about the orientation and the existance of place of birth, and return a structured JSON object.
<instruction>
    Image Type Validation (is_document)
        - Return True only if the image contains a valid front side of KTP card that shows information. Else, the document is not a KTP, return False.
    Orientation
        - Use the position of the head photo and text user information to determine image orientation:
            - If head photo on right and text information on its left = 0
            - If head photo on bottom and text information on top of it (text upside down) = 90 degrees rotated clockwise
            - If head photo on left and text information on the right = 180 degrees rotated clockwise
            - If head photo on top and text information on its below = 270 degrees rotated clockwise
        - This orientation is in clockwise degrees.
        - Think step-by-step about how to determine the orientation based on the image content.
        - Analyze the image and return the orientation as an integer (0, 90, 180, or 270).
    Data Extraction Rules
        - id_number: Must be exactly 16 digits. Refer to 'NIK' in KTP.
        - fullname: Use only uppercase text and match the full name as written on the KTP.
        - date_of_birth: Convert to ISO 8601 format (YYYY-MM-DD). Extract only from valid DOB fields. Refer to 'Tanggal Lahir' in KTP.
        - place_of_birth: Must be a valid city name. Only use existing city names. 'Tempat Lahir' in KTP then convert to UPPERCASE. Think about the existance of the city first, if the place name looks similar to a well-known city, correct minor errors to the most likely valid name.
        - sex: Map "Laki-Laki" to "M", and "Perempuan" to "F". Refer to 'Jenis Kelamin' in KTP.
        - nationality: Usually "WNI" for citizens, "WNA" for foreigners. Convert to uppercase. Refer to 'Kewarganegaraan' in KTP.
    Missing or Unreadable Data
        - If a field is not present or cannot be confidently extracted, return an empty string "".
    Output Format
        - Return a single well-formed JSON object strictly matching the schema.
</instruction>
"""

prompt_extract_data_from_passport = """You are a helpful assistant that extracts information from images of documents.
You will be given an image of a Passport, and your task is to extract the relevant information based on the document type provided.
Your goal is to analyze the image first, give a brief summary what you think especially about the orientation, and return a structured JSON object.
<instruction>
    Image Type Validation (is_document)
        - Return True only if the image contains a valid biographical data page of Passport that shows information. Else, the document is not a Passport, return False.
    Orientation
        - Use the position of the head photo and text to determine image orientation.
        - This orientation is in clockwise degrees.
        - Think step-by-step about how to determine the orientation based on the image content.
        - Analyze the image and return the orientation as an integer (0, 90, 180, or 270).
    Data Extraction Rules
        - id_number: Passport Number must be exactly written on Passport.
        - fullname: Use only uppercase text and match the full name as written on the Passport.
        - date_of_birth: Convert to ISO 8601 format (YYYY-MM-DD). Extract only from valid date of birth fields.
        - place_of_birth: Place of Birth must be exactly written on Passport. Convert to UPPERCASE.
        - sex: "M" for male and "F" for female.
        - nationality: Convert to uppercase using ISO 3166-1 Alpha-2 format which consists of 2 letters.
    Missing or Unreadable Data
        - If a field is not present or cannot be confidently extracted, return an empty string "".
    Output Format
        - Return a single well-formed JSON object strictly matching the schema.
</instruction>
"""

prompt_extract_data_from_ijazah = """You are a helpful assistant that extracts information from images of documents.
You will be given an image of an Ijazah, and your task is to extract the relevant information based on the document type provided.
Your goal is to analyze the image first, give a brief summary what you think especially about the orientation, and return a structured JSON object.
<instruction>
    Image Type Validation (is_document)
        - Return True only if the image contains an Ijazah or SKL (Surat Keterangan Lulus) or any Graduation Certificate of a student. Else, the document is not an Ijazah, return False.
    Orientation
        - Use the position of the head photo and text to determine image orientation.
        - This orientation is in clockwise degrees.
        - Think step-by-step about how to determine the orientation based on the image content.
        - Analyze the image and return the orientation as an integer (0, 90, 180, or 270).
    Data Extraction Rules
        - fullname: Use only uppercase text and match the full name as written on the Ijazah.
        - date_of_birth: Convert to ISO 8601 format (YYYY-MM-DD). Extract only from valid date of birth fields.
        - place_of_birth: Place of Birth must be exactly written on Ijazah. Convert to UPPERCASE.
    Missing or Unreadable Data
        - If a field is not present or cannot be confidently extracted, return an empty string "".
    Output Format
        - Return a single well-formed JSON object strictly matching the schema.
</instruction>
"""

# ----------------- Main LLM Extraction Function ------------------

def extract_data_from_base64_image(base64_image, document_type, prompt_type):

    llm = ChatOpenAI(
        model="gpt-4.1",
        temperature=0.00,
        max_tokens=2048,
        top_p=0.50,
        frequency_penalty=0.00,
        presence_penalty=0.00,
    )

    structured_llm = llm.with_structured_output(document_type)

    extracted_data = structured_llm.invoke(
        [
            {
                "role": "user",
                "content": prompt_type
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "I need you to analyze this image. Identify the orientation of the image. Think first then extract information in this image:"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    },
                ],
            }
        ]
    )
    return extracted_data