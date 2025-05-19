FROM python:3.10-slim

RUN pip install --no-cache-dir pymupdf==1.24.4 fastapi==0.111.0 uvicorn[standard]==0.29.0 pillow==10.3.0
WORKDIR /app
COPY app/main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]