FROM python:3.9-slim

LABEL maintainer="enchant97"

EXPOSE 8000

ENV WORKERS=1
ENV LOG_LEVEL="INFO"
ENV HOST="0.0.0.0"
ENV PORT="8000"

# add curl for health checks
RUN apt-get update \
    && apt-get install -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# setup python environment
COPY requirements.txt requirements.txt

# make sure pip is up to date
RUN ["pip", "install", "pip", "--upgrade"]

# build/add base-requirements
# also allow for DOCKER_BUILDKIT=1 to be used
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

# copy required files
COPY src/web_portal web_portal

# start the server
CMD hypercorn "web_portal.main:create_app()" --bind "$HOST:$PORT" --workers "$WORKERS" --log-level "$LOG_LEVEL"

# built-in health checking
HEALTHCHECK --interval=1m --timeout=30s --retries=3 --start-period=20s \
    CMD curl --fail "http://127.0.0.1:$PORT/is-alive" || exit 1