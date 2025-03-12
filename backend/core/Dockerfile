# # FROM python:3.10-slim

# # WORKDIR /app

# # RUN apt update && apt install -y \
# #     libgl1-mesa-glx \
# #     libglib2.0-0 \
# #     tesseract-ocr \
# #     tesseract-ocr-vie \
# #     && rm -rf /var/lib/apt/lists/*

# # COPY requirements.txt .
# # RUN pip install --no-cache-dir -r requirements.txt

# # RUN pip install opencv-fixer==0.2.5
# # # 2. Chạy opencv-fixer để tự động cấu hình OpenCV
# # RUN python -c "from opencv_fixer import AutoFix; AutoFix()"


# # COPY . .

# # CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "912"]

# FROM python:3.10-slim

# RUN pip install opencv-fixer==0.2.5 && \
#     python -c "from opencv_fixer import AutoFix; AutoFix()"

# WORKDIR /app

# # Cập nhật và cài đặt các gói hệ thống cần thiết cho OpenCV
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libgl1-mesa-glx \
#     libglib2.0-0 \
#     libsm6 \
#     libxext6 \
#     libxrender1 \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Copy file requirements và cài đặt các thư viện Python
# COPY requirements.txt .
# RUN pip install --upgrade pip && \
#     pip install --no-cache-dir -r requirements.txt && \
# # Copy toàn bộ mã nguồn vào container
# COPY . .

# # Chạy ứng dụng với uvicorn
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "912"]

FROM python:3.10-slim
# Cập nhật và cài đặt các gói cần thiết cho việc build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Sao chép file requirements (chứa opencv-python-headless)
COPY requirements.txt .

# Cài đặt dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép code vào container
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "912"]