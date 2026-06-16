# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder

WORKDIR /build
RUN python -m venv /opt/venv
COPY src/ai_service/requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Cài đặt thư viện đồ họa cho OpenCV/YOLO
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=builder /opt/venv /opt/venv
COPY src/ai_service/ ./src/ai_service/

# Thư mục lưu YOLO weights (cấp quyền cho appuser)
RUN mkdir -p /app/weights && chown -R appuser:appgroup /app

USER appuser

EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:9000/health', timeout=3).read()" || exit 1

CMD ["sh", "-c", "uvicorn src.ai_service.main:app --host 0.0.0.0 --port 9000"]