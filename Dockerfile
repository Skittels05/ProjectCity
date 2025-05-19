# ---- Билд этап ----
FROM python:3.13 AS builder
LABEL authors="Asriel_Story"
COPY requirements.txt .

RUN pip install --user -r requirements.txt

# ---- Финальный этап ----
FROM python:3.13-slim
WORKDIR /app

VOLUME /app/uploads

COPY --from=builder /root/.local /root/.local
COPY ./src .

ENV PATH=/root/.local:$PATH

ARG DOMAIN
ENV DOMAIN=$DOMAIN
ARG PORT
ENV PORT=$PORT
ARG SSL_KEYFILE
ENV SSL_KEYFILE=$SSL_KEYFILE
ARG SSL_CERTFILE
ENV SSL_CERTFILE=$SSL_CERTFILE
ARG DATABASE_URL
ENV DATABASE_URL=$DATABASE_URL
ARG REDIS_URL
ENV REDIS_URL=$REDIS_URL
ARG EMAIL_DOMAIN
ENV EMAIL_DOMAIN=$EMAIL_DOMAIN
ARG USE_TLS
ENV USE_TLS=$USE_TLS

EXPOSE 8000 8000

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

HEALTHCHECK --interval=30s --timeout=5s CMD curl http://0.0.0.0:8000/api/health || exit 1

CMD ["python", "main.py"]
