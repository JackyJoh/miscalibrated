# backend/Dockerfile — builds the FastAPI application image
FROM python:3.12-slim

WORKDIR /app

# Install system deps needed by confluent-kafka (librdkafka)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Start the FastAPI app with uvicorn
# --reload is for development only; remove in production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
