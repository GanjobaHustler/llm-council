FROM python:3.10-slim

# Install Node.js 20
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies explicitly (avoids pyproject build-backend issues)
RUN pip install --no-cache-dir \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.32.0" \
    "python-dotenv>=1.0.0" \
    "httpx>=0.27.0" \
    "pydantic>=2.9.0" \
    "aiofiles>=24.1.0"

# Build the React frontend
RUN cd frontend && npm ci && npm run build

# Railway injects $PORT at runtime
ENV PORT=8001
EXPOSE 8001

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001}"]
