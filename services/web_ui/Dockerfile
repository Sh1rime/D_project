FROM python:3.10-slim

RUN pip install --no-cache-dir \
        fastapi==0.111.0 uvicorn[standard]==0.29.0 \
        python-multipart==0.0.9 jinja2==3.1.3 requests==2.32.3 \
        aiofiles==23.2.1   
WORKDIR /app
COPY app .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
