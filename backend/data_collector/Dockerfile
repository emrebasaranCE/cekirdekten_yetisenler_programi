# 1 . Use the official Python image
FROM python:3.13-slim

# 2. Install curl to check health of the service
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 3. Set working directory
WORKDIR /app

# 4. Copy & install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy service code
COPY app.py config.py ./

# 6. Expose the port from config.py (default 5001) :contentReference[oaicite:0]{index=0}
EXPOSE 5001

# 7. Run the service (unbuffered logs)
CMD ["python", "-u", "app.py"]
