FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    xvfb \
    x11-utils \
    xdotool \
    scrot \
    imagemagick \
    python3-tk \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    libjpeg-dev \
    python3-dev \
    python3-numpy \
    libsdl2-2.0-0 \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set up Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set up working directory
WORKDIR /app

# Copy game files
COPY game.py .
COPY automation.py .
# COPY sprites/ ./sprites/
COPY game/sprites/ ./sprites/

# Set environment variables for display
ENV DISPLAY=:99

# Create script to start virtual display and run automation
COPY start.sh .
RUN chmod +x start.sh

# Expose directory for screenshots
VOLUME ["/app/screenshots"]

# Default command
CMD ["./start.sh"]
