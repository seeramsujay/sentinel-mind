FROM python:3.11-slim

WORKDIR /app

# Copy requirement files first
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project (backend and scripts)
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Cloud Run entrypoint
CMD exec python main.py
