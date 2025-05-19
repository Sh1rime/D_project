FROM python:3.10-slim

# 1. Системные зависимости
RUN apt-get update -o Acquire::Retries=3 --fix-missing && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng \
        libleptonica-dev libtesseract-dev  \
        && rm -rf /var/lib/apt/lists/*

# 2. Python
RUN pip install --no-cache-dir \
        fastapi==0.111.0 uvicorn[standard]==0.29.0 \
        pytesseract==0.3.10 pillow==10.3.0 opencv-python-headless==4.10.0.82

WORKDIR /app
COPY app/main.py .
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9100"]
