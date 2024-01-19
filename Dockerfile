# syntax=docker/dockerfile:1.4
ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-alpine as builder

    WORKDIR /app

    COPY . .

    RUN python -m venv .venv
    ENV PATH="/app/.venv/bin:$PATH"

    RUN --mount=type=cache,target=/root/.cache pip install .

FROM python:${PYTHON_VERSION}-alpine

    WORKDIR /app
    EXPOSE 8000
    ENV PATH="/app/.venv/bin:$PATH"
    ENV WORKERS=1
    ENV LOG_LEVEL="INFO"
    ENV HOST="0.0.0.0"
    ENV PORT="8000"
    ENV PLUGINS_PATH="/app/plugins"
    ENV DATA_PATH="/app/data"

    COPY LICENSE.txt THIRD-PARTY.txt ./

    COPY --from=builder --link /app/.venv .venv

    COPY plugins plugins

    COPY scripts/* ./

    CMD /bin/sh run.sh

    HEALTHCHECK --interval=1m --start-period=30s \
        CMD /bin/sh health-check.sh
