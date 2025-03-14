FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget=1.20.3-1ubuntu2 \
    netcat-traditional=1.10-41.1 \
    gnupg=2.2.19-3ubuntu2.1 \
    curl=7.68.0-1ubuntu2.6 \
    unzip=6.0-25ubuntu1.1 \
    xvfb=2:1.20.9-2ubuntu1.6 \
    libgconf-2-4=3.2.6-6 \
    libxss1=1:1.2.3-1build1 \
    libnss3=2:3.49.1-1ubuntu1.5 \
    libnspr4=2:4.25-1 \
    libasound2=1.2.2-2.1ubuntu2.5 \
    libatk1.0-0=2.35.1-1ubuntu2 \
    libatk-bridge2.0-0=2.34.2-0ubuntu2 \
    libcups2=2.3.1-9ubuntu1.1 \
    libdbus-1-3=1.12.16-2ubuntu2.1 \
    libdrm2=2.4.101-2ubuntu1.2 \
    libgbm1=20.0.8-0ubuntu1~20.04.1 \
    libgtk-3-0=3.24.20-0ubuntu1 \
    libxcomposite1=1:0.4.5-1 \
    libxdamage1=1:1.1.5-2 \
    libxfixes3=1:5.0.3-2 \
    libxrandr2=2:1.5.2-0ubuntu1 \
    xdg-utils=1.1.3-2ubuntu1.20.04.2 \
    fonts-liberation=1:1.07.4-11 \
    dbus=1.12.16-2ubuntu2.1 \
    xauth=1:1.1-0ubuntu1 \
    x11vnc=0.9.13-6 \
    tigervnc-tools=1.10.1+dfsg-3 \
    supervisor=4.2.2-2ubuntu0.1 \
    net-tools=1.60+git20180626.aebd88e-1ubuntu1 \
    procps=2:3.3.16-1ubuntu2.3 \
    git=1:2.25.1-1ubuntu3.10 \
    python3-numpy=1:1.17.4-5ubuntu3.1 \
    fontconfig=2.13.1-2ubuntu3 \
    fonts-dejavu=2.37-1 \
    fonts-dejavu-core=2.37-1 \
    fonts-dejavu-extra=2.37-1 \
    && rm -rf /var/lib/apt/lists/*

# Install noVNC
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc \
    && git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify \
    && ln -s /opt/novnc/vnc.html /opt/novnc/index.html

# Set platform for ARM64 ▋
