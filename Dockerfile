FROM python:3.12-slim

WORKDIR /app

# Install Tesseract
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr libtesseract-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy source
COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]