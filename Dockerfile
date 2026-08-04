FROM python:3.12-slim

WORKDIR /app

# Install base dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Copy project configuration
COPY pyproject.toml ./

# If using a virtual environment or specific package manager, insert here
# For now, a standard pip install of the project
RUN pip install --no-cache-dir . || echo "No dependencies to install yet"

# Copy source code
COPY src/ ./src/

# Entry point placeholder (to be updated as interface_layer evolves)
CMD ["python", "-c", "print('AI Workspace Bridge Initialized')"]
