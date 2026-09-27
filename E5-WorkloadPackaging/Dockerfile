FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy application script
COPY webServer.py .

# Expose HTTP port
EXPOSE 8000

# Run HTTP server without buffering output
CMD ["python", "-u", "webServer.py"]
