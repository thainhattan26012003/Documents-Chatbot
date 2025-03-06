# Dockerfile
FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y tesseract-ocr tesseract-ocr-vie libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt
EXPOSE 8081
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081", "--reload"]
