# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.10.0
FROM python:${PYTHON_VERSION}-bullseye AS base

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy project files
COPY ./ /app/

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc python3-dev libffi-dev build-essential \
    libsdl2-2.0-0 libsdl2-dev libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0 \
    libsm6 libxrender1 libxext6 libgl1-mesa-glx \
    xvfb alsa-utils alsa-oss alsa-tools \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "/app/createDatabase.py"]

# Set default user
USER root
