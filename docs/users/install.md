# Install
This sections will guide you though installing web-portal.

- It is written for Docker users, although can be adapted for other systems.
- It will assume you have Docker and Docker Compose installed.
- Is recommended to install behind a reverse proxy like Nginx for custom routing and domain names.
- Plugins may require more configs to be set

## Selecting A Database
First you will need to decide which database to use:

- SQLite
- MySQL

If you only have a small amount of users and have no experience, its best to stick with SQLite.

## Configure
Now we can configure web-portal. We can do this using Docker Compose. So we will need to create a compose file.

This file should be placed in a directory where you are going to store all your app data. The following is an example of your directory layout:

```
web_portal/
    docker-compose.yml
    data/
```

### Example Compose File
This is an example config (using SQLite) which you can copy, as long as `SECRET_KEY` value is changed for security.

```yaml
version: "3"

services:
  web-portal:
    container_name: web-portal
    image: ghcr.io/enchant97/web-portal:2
    restart: unless-stopped
    volumes:
      - ./data:/data
    ports:
      # Change only left side
      - 8000:8000
    environment:
      - "DATA_PATH=/data"
      - "DB_URI=sqlite:///data/db.sqlite"
      # This must be secure
      - "SECRET_KEY=replace_me_123"
```

### Environment Variables
All configs shown here should be given as environment variables.

| Name           | Description                            | Default              |
| :------------- | :------------------------------------- | :------------------- |
| DB_URI         | URI of where db is stored              |                      |
| DATA_PATH      | Where plugin & app data will be stored |                      |
| SECRET_KEY     | Your app secret (use something secure) | (randomly generated) |
| SECURE_COOKIES | Whether to require https for cookies   | False                |
| LOG_LEVEL      | What log level to use                  | "INFO"               |

> SECRET_KEY should be set, otherwise logins will be reset on server restart

This table shows how the `DB_URI` values should look:

| Database | URI Format                              |
| :------- | :-------------------------------------- |
| MySQL    | mysql://user:password@hostname/database |
| SQLite   | sqlite://path-to-database.db            |

Other configs related to when running through the official docker image:

| Name      | Description                           | Default |
| :-------- | :------------------------------------ | :------ |
| WORKERS   | Number of separate processes to spawn | 1       |
| CERT_FILE | SSL certificate file path (public)    | -       |
| KEY_FILE  | SSL key file path (private)           | -       |

> Default values indicated with '-' are not required

> If you want HTTPS, both `CERT_FILE` and `KEY_FILE` environment values must be provided to valid certificates

## Initial Run
Now a compose file has been created, we can finally download and run the Docker image.

Inside the app directory, run these commands

> Running `docker compose pull` ensures you have the latest specified in the compose file

> The `-d` argument runs the app in the background

```
docker compose pull
docker compose up -d
```

After these have been run, navigate in the browser to the hostname and port you configured. From there you should see a setup wizard which will guide you through the rest of the install.

If you have a question, you can ask in the GitHub discussions page at: <https://github.com/enchant97/web-portal/discussions>.
