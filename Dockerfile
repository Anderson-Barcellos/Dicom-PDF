# syntax=docker/dockerfile:1

# Frontend build stage
FROM node:20 AS frontend-build
WORKDIR /app/webapp
COPY webapp/package*.json ./
RUN npm install
COPY webapp .
RUN npm run build

# Runtime stage
FROM python:3.11-slim
WORKDIR /app

# System dependencies for OpenCV and Tesseract
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       tesseract-ocr libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy built frontend
COPY --from=frontend-build /app/webapp/dist ./webapp/dist

CMD ["python", "main.py"]
