# Deployment

[Home](index.md)

## Notes
- Make sure to run as a non-root user
- The program has been designed to run with mysql/mariadb and sqlite. _You can get postgres working but it will require modification of the requirements file_ 
- It is designed to run with a proxy
- The development server can be run with `python -m src.web_portal`

## Without Docker
1. To run this app you should have all the python requirements
2. Setup configs either with a .env file or environment variables (or both)
3. Run the app using hypercorn (or something similar)
4. Use a reverse proxy like [nginx](https://nginx.org/)

## With [Docker](https://www.docker.com/)
1. create the docker image using the Dockerfile
2. Setup configs either with a .env file or environment variables (or both)
3. Run docker container, or you could use docker-compose with [nginx](https://nginx.org/)
