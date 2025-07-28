# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies for PDF parsing
RUN apt-get update && \
    apt-get install -y gcc libxml2-dev libxslt-dev libjpeg-dev zlib1g-dev poppler-utils && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy local code to container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Default command
CMD ["python", "process_pdfs.py"]
