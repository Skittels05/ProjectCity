# ---- Билд этап ----
FROM python:3.13 AS builder
LABEL authors="Asriel_Story"
COPY requirements.txt .

RUN pip install --user -r requirements.txt

# ---- Финальный этап ----
FROM python:3.13-slim
WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY ./src .

ENV PATH=/root/.local:$PATH

EXPOSE 8000 8000

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

HEALTHCHECK --interval=30s --timeout=5s CMD curl http://0.0.0.0:8000/api/health || exit 1

CMD ["python", "main.py"]
