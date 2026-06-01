# Use a lightweight Python image
FROM python:3.12-slim

# Prevent Python from writing .pyc files + enable logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

RUN apt-get update && apt-get install curl nano -y && rm -rf /var/lib/apt/lists/*

# Install dependencies first (better caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Flask port
EXPOSE 5000

# Start the app
CMD ["python", "app.py"]