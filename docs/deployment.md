# Deployment

[Home](index.md)

## Without Docker
1. To run this app you should have all the python requirements
2. Setup configs either with a .env file or environment variables (or both)
3. Easily run the app as `python -m web_portal`.
This is will run using [Hypercorn](https://pypi.org/project/Hypercorn/)
with the given configs
4. Use a reverse proxy like [nginx](https://nginx.org/)

## With [Docker](https://www.docker.com/)
1. create the docker image using the Dockerfile
2. Setup configs either with a .env file or environment variables (or both)
3. Run docker container, or you could use docker-compose with [nginx](https://nginx.org/)
