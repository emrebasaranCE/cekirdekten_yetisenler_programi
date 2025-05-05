# 1. Base image
FROM python:3.13-slim

# 2. Install curl to check health of the service
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 3. Set working directory
WORKDIR /app

# 4. Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy service code
COPY app.py config.py anomaly_detection.py ./

# 6. Expose the HTTP port (from config.py default PORT=5002)
EXPOSE 5002

# 7. Run the service
#    -u for unbuffered stdout (real-time logs)
CMD ["python", "-u", "app.py"]
