FROM python:3.10-slim

# Cập nhật và cài đặt các thư viện hệ thống cần thiết cho OpenCV và Tesseract OCR
RUN apt update && apt install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-vie \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

# 1. Tải và cài đặt công cụ opencv-fixer
RUN pip install opencv-fixer==0.2.5
# 2. Chạy opencv-fixer để tự động cấu hình OpenCV
RUN python -c "from opencv_fixer import AutoFix; AutoFix()"

# COPY . .

CMD [ "streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=none" ]
