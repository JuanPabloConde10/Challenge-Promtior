FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    KMP_DUPLICATE_LIB_OK=TRUE \
    UV_SYSTEM_PYTHON=1 \
    UV_CACHE_DIR=/tmp/uv-cache

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv pip compile pyproject.toml -o /tmp/requirements.txt \
    && uv pip install --system -r /tmp/requirements.txt \
    && rm -rf /root/.cache /tmp/uv-cache


FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    KMP_DUPLICATE_LIB_OK=TRUE

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY . .

EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
