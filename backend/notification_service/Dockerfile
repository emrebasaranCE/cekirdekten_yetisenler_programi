# 1. Base image
FROM python:3.13-slim

# 2. Install curl to check health of the service
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 3. Set working directory
WORKDIR /app

# 4. Install system dependencies (if you need any, e.g. build-essential),
#    here kept minimal; adjust as needed.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy service code
COPY app.py config.py ./

# 7. Expose the HTTP/WebSocket port from config.py (default 5003)
EXPOSE 5003

# 8. Run the service
#    -u ensures logs are unbuffered for real-time output
CMD ["python", "-u", "app.py"]
