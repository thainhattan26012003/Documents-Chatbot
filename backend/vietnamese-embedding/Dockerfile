FROM nvcr.io/nvidia/pytorch:23.05-py3

ENV DEBIAN_FRONTEND=noninteractive

# Cập nhật và cài đặt tất cả các gói cần thiết chỉ với 1 lệnh RUN
RUN apt-get update && \
    apt-get install -y \
        zip \
        htop \
        screen \
        libgl1-mesa-glx \
        libfreetype6-dev \
        libglib2.0-0 \
        libglib2.0-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

# Nâng cấp pip và cài đặt các thư viện Python
RUN pip install --upgrade pip && pip install -r requirements.txt