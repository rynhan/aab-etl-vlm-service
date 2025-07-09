FROM python:3.11-slim

# System deps for pdf2image/poppler (very important!)
RUN apt-get update && apt-get install -y poppler-utils && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install them first (for Docker build cache efficiency)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and env file
COPY ./app ./app
COPY .env .env

# Expose default uvicorn port
EXPOSE 8000

# Entrypoint
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]