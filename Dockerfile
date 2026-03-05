# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies and clean up
RUN apt-get update && \
    apt-get install -y openssl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for certificates
RUN mkdir -p /app/certs

# Copy the current directory contents into the container at /app
COPY . .

# Generate self-signed certificates if needed
RUN if [ ! -f /app/certs/cert.pem ] || [ ! -f /app/certs/key.pem ]; then \
    openssl req -x509 -newkey rsa:4096 -keyout /app/certs/key.pem -out /app/certs/cert.pem -days 365 -nodes \
    -subj "/CN=localhost" -addext "subjectAltName = DNS:localhost,IP:127.0.0.1"; \
    fi

# Make ports 8000 and 8443 available to the world outside this container
EXPOSE 8000 8443

# Define default command to run the application
# Use HTTP by default, but user can override with --https via docker-compose
CMD ["python", "-m", "fasty.main"]
