# syntax=docker/dockerfile:1
FROM python:3.11-slim
WORKDIR /app

# System dependencies for OpenCV and Tesseract
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       tesseract-ocr libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
