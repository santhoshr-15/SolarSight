FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for OpenCV/Ultralytics
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and model
COPY app/ app/
COPY model/ model/

# Expose default port
EXPOSE 8000

# Start FastAPI using uvicorn (defaults to CPU inference inside the container unless configured otherwise)
# Uses shell form to support Render's dynamic $PORT environment variable, falling back to 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
