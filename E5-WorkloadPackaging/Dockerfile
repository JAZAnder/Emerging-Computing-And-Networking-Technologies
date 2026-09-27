FROM python:3.10-slim

#Set working directory
WORKDIR /app

# Copy python  script
COPY webServer.py .

# Expose Web Server port
EXPOSE 8000

# Run HTTP server
CMD ["python", "-u", "webServer.py"]
