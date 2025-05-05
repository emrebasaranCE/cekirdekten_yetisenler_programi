# 1 . Use the official Python image
FROM python:3.13-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy & install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy service code
COPY app.py config.py ./

# 5. Expose the port from config.py (default 5001) :contentReference[oaicite:0]{index=0}
EXPOSE 5001

# 6. Run the service (unbuffered logs)
CMD ["python", "-u", "app.py"]
