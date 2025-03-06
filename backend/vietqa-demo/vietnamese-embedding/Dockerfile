# Use the NVIDIA PyTorch base image
FROM nvcr.io/nvidia/pytorch:23.05-py3

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && \
    apt-get install -y zip htop screen libgl1-mesa-glx libfreetype6-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN /usr/bin/python -m pip install --upgrade pip

# Set the working directory in the container
WORKDIR /app

# Install system dependencies including libGL
RUN apt-get update && apt-get install -y libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

# Install system dependencies: libGL for OpenGL support, and both libglib2.0-0 and libglib2.0-dev for GLib (which includes libgthread-2.0)
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx libglib2.0-0 libglib2.0-dev && \
    rm -rf /var/lib/apt/lists/*

COPY . .
# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# 1. download the autofix tool
RUN pip install opencv-fixer==0.2.5
# 2. execute
RUN python -c "from opencv_fixer import AutoFix; AutoFix()"

# Expose port 7860 for the Gradio app
#EXPOSE 7860