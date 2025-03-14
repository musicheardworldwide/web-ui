FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget=1.20.3-1+deb10u2 \
    netcat-traditional=1.10-41.1 \
    gnupg=2.2.12-1+deb10u1 \
    curl=7.64.0-4+deb10u2 \
    unzip=6.0-23+deb10u1 \
    xvfb=2:1.20.4-1+deb10u2 \
    libgconf-2-4=3.2.6-5 \
    libxss1=1:1.2.3-1 \
    libnss3=2:3.42.1-1+deb10u3 \
    libnspr4=2:4.20-1 \
    libasound2=1.1.8-1 \
    libatk1.0-0=2.30.0-2 \
    libatk-bridge2.0-0=2.30.0-2 \
    libcups2=2.2.10-6+deb10u5 \
    libdbus-1-3=1.12.20-0+deb10u1 \
    libdrm2=2.4.97-1+deb10u1 \
    libgbm1=18.3.6-2+deb10u1 \
    libgtk-3-0=3.24.5-1 \
    libxcomposite1=1:0.4.4-2 \
    libxdamage1=1:1.1.4-3+b3 \
    libxfixes3=1:5.0.3-1 \
    libxrandr2=2:1.5.1-1 \
    xdg-utils=1.1.3-1+deb10u1 \
    fonts-liberation=1:1.07.4-9 \
    dbus=1.12.20-0+deb10u1 \
    xauth=1:1.0.10-1 \
    x11vnc=1.0.12-2 \
    tigervnc-tools=1.9.0+dfsg-3 \
    supervisor=3.3.5-1 \
    net-tools=1.60+git20180626.aebd88e-1 \
    procps=2:3.3.15-2 \
    git=1:2.20.1-2+deb10u3 \
    python3-numpy=1:1.16.2-1 \
    fontconfig=2.13.1-2 \
    fonts-dejavu=2.37-1 \
    fonts-dejavu-core=2.37-1 \
    fonts-dejavu-extra=2.37-1 \
    && rm -rf /var/lib/apt/lists/*

# Install noVNC
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc \
    && git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify \
    && ln -s /opt/novnc/vnc.html /opt/novnc/index.html

# Set platform for ARM64 compatibility
ARG TARGETPLATFORM=linux/amd64

# Set up working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers with system dependencies
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN playwright install --with-deps chromium && playwright install-deps

# Copy the application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV BROWSER_USE_LOGGING_LEVEL=info
ENV CHROME_PATH=/ms-playwright/chromium-*/chrome-linux/chrome
ENV ANONYMIZED_TELEMETRY=false
ENV DISPLAY=:99
ENV RESOLUTION=1920x1080x24
ENV VNC_PASSWORD=Dullownation123!
ENV CHROME_PERSISTENT_SESSION=true
ENV RESOLUTION_WIDTH=1920
ENV RESOLUTION_HEIGHT=1080

# Set up supervisor configuration
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 7788 6080 5901

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
