FROM ubuntu:22.04

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && apt-get install -y \
    supervisor \
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    wget \
    unzip \
    libxcursor1 \
    libxinerama1 \
    libgl1 \
    libglu1-mesa \
    libasound2 \
    libpulse0 \
    libudev1 \
    libxi6 \
    libxrandr2 \
    mesa-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create directory for Godot
RUN mkdir -p /godot

# Download and install Godot Server version (headless) which is more compatible with containers
RUN wget https://github.com/godotengine/godot/releases/download/4.2.1-stable/Godot_v4.2.1-stable_linux_server.64.zip -O /tmp/godot.zip \
    && unzip /tmp/godot.zip -d /tmp \
    && mv /tmp/Godot_v4.2.1-stable_linux_server.64 /godot/godot \
    && chmod +x /godot/godot \
    && rm /tmp/godot.zip

# Set up VNC password
RUN mkdir -p /root/.vnc
RUN x11vnc -storepasswd password /root/.vnc/passwd

# Copy supervisord configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports
EXPOSE 6080 5900

# Set environment variables for OpenGL
ENV LIBGL_ALWAYS_SOFTWARE=1

# Start supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 