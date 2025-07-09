
# ETL VLM Document AI Service

A scalable FastAPI-based service for extracting document data from pictures (KTP, passport, ijazah, etc.) using advanced Vision Language Model (VLM).

---

## Features

- Extract and validate data from Indonesian ID cards (KTP), Passports, and Ijazah/Graduation Certificates
- Supports image and PDF input (via URL)
- Auto-orientation correction of scanned/photos
- Standardized JSON output
- Ready for containerized and cloud/on-prem deployment
- Swagger/OpenAPI docs

---

## Technologies Used

- FastAPI (REST API)
- Python 3.11
- LangChain (with OpenAI/ChatGPT)
- Pillow, pdf2image, requests
- Docker & Docker Compose (for easy deployment)

---

## Project Structure

```
etl-vlm-service/
├── app/
│   ├── main.py               # FastAPI bootstrap
│   ├── api.py                # API routes
│   ├── schemas.py            # Pydantic request/response models
│   ├── service.py            # Orchestrates preprocessing & LLM extraction
│   ├── extractor/
│   │   ├── preprocessor.py   # File download, conversion, image rotation
│   │   └── llm_extract.py    # LLM prompts & schema enforcement
│   └── config.py             # Environment/settings loader
├── tests/
│   └── test_service.py       # Unit & integration tests (pytest)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env                      # (Not in repo!) API keys/config variables
└── README.md
```

---

## Getting Started

### 1. **Clone the Repository**
```bash
git clone https://github.com/your-org/etl-vlm-service.git
cd etl-vlm-service
```

### 2. **Configure Environment Variables**
Create a `.env` file (never commit credentials!):

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxx
ALLOWED_ORIGINS=http://localhost,http://your-campus-domain.edu
```

### 3. **Build & Run Locally (Docker)**
**A. Build the image:**
```bash
docker build -t etl-vlm-service:latest .
```

**B. Run the service:**
```bash
docker run -p 8000:8000 --env-file .env etl-vlm-service:latest
```

### 4. **Or use Docker Compose**
```bash
docker compose up --build
```
*(needs a `docker-compose.yml` in the root)*

---

## API Usage

### **Interactive Docs**
- Visit: [http://localhost:8000/docs](http://localhost:8000/docs) for a Swagger UI interface

### **Main Endpoint**

`POST /api/extract-data`

**Request Body:**
```json
{
  "url": "https://example.com/my-ktp.pdf",  // or .jpg/.png
  "doc_type": "ktp"                         // or "passport", "ijazah"
}
```

**Response (Example):**
```json
{
  "is_document": true,
  "orientation": 0,
  "id_number": "3201xxxxxxxxxxxx",
  "fullname": "JOHN DOE",
  "date_of_birth": "2000-01-01",
  "place_of_birth": "BANDUNG",
  "sex": "M",
  "nationality": "WNI",
  "message": null
}
```

### **Document Types**
- `"ktp"`
- `"passport"`
- `"ijazah"`

---

## Development & Running Tests

### **Install Python Requirements**
```bash
pip install -r requirements.txt
```

### **Run Unit Tests**
```bash
pytest
```

### **Run API Locally (without Docker)**
```bash
uvicorn app.main:app --reload --env-file .env
```

---

## Common Issues

- **OPENAI_API_KEY error:**  
  Ensure your `.env` file is present and contains a valid API key.
- **pdf2image errors:**  
  Install poppler-utils on your system (`apt-get install poppler-utils` for Ubuntu/Debian, already handled if using Dockerfile).
- **CORS problems:**  
  Set `ALLOWED_ORIGINS` in your `.env` for your client’s domain.

---

## Customization

- **Add new document types:**  
  Define schema & prompt in `app/extractor/llm_extract.py`, update `service.py`, and map endpoints as needed.
- **Internal endpoints:**  
  Add new routers to `api.py` as your use case grows.

---

## Contribution

PRs and issues welcome! Please fork and submit a pull request.

---

## License

MIT (I guess ¯\\_(ツ)_/¯)

---

## Maintainer

- Me


---