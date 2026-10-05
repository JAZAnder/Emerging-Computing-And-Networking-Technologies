FROM python:3.10-slim

# Install required networking utilities and HTTP client
RUN apt-get update && apt-get install -y \
    net-tools \
    iproute2 \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*