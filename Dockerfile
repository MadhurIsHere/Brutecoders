# Base image: Python 3.10 (Covering most Python needs)
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
# - git: for git operations (if needed inside)
# - curl: for installing node
# - build-essential: for compiling code (gcc, make, etc.)
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18 (LTS) - Covering JS/TS needs
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Create a working directory
WORKDIR /app

# Upgrade pip and install common test runners globally
RUN pip install --no-cache-dir --upgrade pip pytest pytest-cov
# Install common JS test runners globally
RUN npm install -g jest mocha

# Default command (can be overridden)
CMD ["tail", "-f", "/dev/null"]
