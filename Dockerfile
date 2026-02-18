FROM python:3.10-slim

# Install Node.js 20
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies (from pyproject.toml via pip)
RUN pip install --no-cache-dir -e .

# Build the React frontend
RUN cd frontend && npm ci && npm run build

# Railway injects $PORT at runtime
ENV PORT=8001
EXPOSE 8001

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001}
