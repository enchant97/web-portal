FROM python:3.9-slim as builder

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python -m venv .venv

# also allow for DOCKER_BUILDKIT=1 to be used
RUN --mount=type=cache,target=/root/.cache ./.venv/bin/pip install -r requirements.txt

FROM python:3.9-alpine3.14

WORKDIR /app
EXPOSE 8000
ENV WORKERS=1
ENV LOG_LEVEL="INFO"
ENV HOST="0.0.0.0"
ENV PORT="8000"

COPY --from=builder /app/.venv .venv

COPY src/web_portal web_portal

CMD ./.venv/bin/hypercorn 'web_portal.main:create_app()' --bind "$HOST:$PORT" --workers "$WORKERS" --log-level "$LOG_LEVEL"

HEALTHCHECK --interval=1m --start-period=30s \
    CMD ./.venv/bin/python -m web_health_checker 'http://127.0.0.1:8000/is-healthy'
