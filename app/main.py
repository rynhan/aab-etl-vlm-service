# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router  # import the router from api.py
import os

# Load allowed origins from environment or set default
# ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost, http://127.0.0.1").split(",")

app = FastAPI(
    title="Document Extraction AI Service",
    description="Extracts and validates document data (KTP, Passport, Ijazah) using AI for student onboarding.",
    version="1.0.0",
)

# CORS settings (Edit allowed origins as necessary for your IS needs)
app.add_middleware(
    CORSMiddleware,
    # allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS],  # list of origins
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")
