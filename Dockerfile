FROM python:3.9.1-alpine

LABEL maintainer="enchant97"

EXPOSE 8000

# add curl for health checks
RUN apk add curl

# setup python environment
COPY requirements.txt requirements.txt

# make sure pip is up to date
RUN ["pip", "install", "pip", "--upgrade"]

# build/add base-requirements
RUN ["pip", "install", "-r", "requirements.txt"]

# copy required files
COPY src/web_portal web_portal

# start the server
CMD python -m web_portal