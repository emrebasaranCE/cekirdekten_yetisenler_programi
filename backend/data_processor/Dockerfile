# 1. Base image
FROM python:3.13-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy service code
COPY app.py config.py anomaly_detection.py ./

# 5. Expose the HTTP port (from config.py default PORT=5002)
EXPOSE 5002

# 6. Run the service
#    -u for unbuffered stdout (real-time logs)
CMD ["python", "-u", "app.py"]
