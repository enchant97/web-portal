ARG PYTHON_VERSION=3.10

FROM python:${PYTHON_VERSION}-slim as builder

    WORKDIR /app

    COPY requirements.txt requirements.txt

    RUN python -m venv .venv
    ENV PATH="/app/.venv/bin:$PATH"

    # caching with DOCKER_BUILDKIT=1
    RUN --mount=type=cache,target=/root/.cache pip install -r requirements.txt

FROM python:${PYTHON_VERSION}-alpine

    WORKDIR /app
    EXPOSE 8000
    ENV PATH="/app/.venv/bin:$PATH"
    ENV WORKERS=1
    ENV LOG_LEVEL="INFO"
    ENV HOST="0.0.0.0"
    ENV PORT="8000"
    ENV UNSECURE_LOGIN=1

    COPY --from=builder /app/.venv .venv

    COPY src/web_portal web_portal

    CMD hypercorn 'web_portal.main:create_app()' --bind "$HOST:$PORT" --workers "$WORKERS" --log-level "$LOG_LEVEL"

    HEALTHCHECK --interval=1m --start-period=30s \
        CMD python -m web_health_checker 'http://127.0.0.1:$PORT/is-healthy'
