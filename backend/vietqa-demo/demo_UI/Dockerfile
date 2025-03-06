FROM python:3.10-slim

WORKDIR /app

RUN apt update && apt install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-vie \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install opencv-fixer==0.2.5
# 2. Chạy opencv-fixer để tự động cấu hình OpenCV
RUN python -c "from opencv_fixer import AutoFix; AutoFix()"


COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "912"]
