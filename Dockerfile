# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.10.0
FROM python:${PYTHON_VERSION}-bullseye AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app
# Copy the source code into the container.
COPY ./ /app/

RUN apt-get update && apt-get install -y \
    gcc python3-dev libffi-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Install dependencies required for pygame
#RUN apt-get update && apt-get install -y \
#    gcc musl-dev python3-dev libffi-dev build-essential \
#    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    libsdl2-2.0-0 libsdl2-dev libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0 \
    libsm6 libxrender1 libxext6 libgl1-mesa-glx \
    xvfb alsa-utils alsa-oss alsa-tools \
    && rm -rf /var/lib/apt/lists/*

# Install pygame 2.6.1
RUN pip install pygame==2.6.1

RUN pip install flask python-jose flasgger

RUN pip install requests

COPY . .

USER root
