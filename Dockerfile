# syntax=docker/dockerfile:1.4
ARG PYTHON_VERSION=3.14
ARG ALPINE_VERSION=3.24

FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION} as builder

    COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

    WORKDIR /app

    ENV PYTHONUNBUFFERED=1
    ENV UV_NO_DEV=1
    ENV UV_PYTHON_DOWNLOADS=0
    ENV UV_COMPILE_BYTECODE=1
    ENV UV_LINK_MODE=copy

    RUN --mount=type=cache,target=/root/.cache/uv \
        --mount=type=bind,source=uv.lock,target=uv.lock \
        --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
        uv sync --locked --no-install-project --no-editable

    COPY . .

    RUN --mount=type=cache,target=/root/.cache/uv \
        uv sync --locked --no-editable


FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION}

    WORKDIR /app
    EXPOSE 8000
    ENV PATH="/app/.venv/bin:$PATH"
    ENV WORKERS=1
    ENV LOG_LEVEL="INFO"
    ENV HOST="0.0.0.0"
    ENV PORT="8000"
    ENV PLUGINS_PATH="/app/plugins"
    ENV DATA_PATH="/app/data"
    ENV DB_URI="sqlite:///app/data/db.sqlite"
    VOLUME [ "/app/data" ]

    COPY LICENSE.txt THIRD-PARTY.txt ./

    COPY --from=builder --link /app/.venv .venv

    COPY plugins plugins

    COPY scripts/* ./

    CMD /bin/sh run.sh

    HEALTHCHECK --interval=1m --start-period=30s \
        CMD /bin/sh health-check.sh
