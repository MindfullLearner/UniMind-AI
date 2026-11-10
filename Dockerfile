
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create writable log directory
RUN mkdir -p /app/logs \
    && useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000
EXPOSE 8501

# Default service: FastAPI backend
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
