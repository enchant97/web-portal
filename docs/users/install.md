# Install
This sections will guide you though installing web-portal.

- If following the Docker guide it is expected you have Docker and Docker Compose installed
- If following without Docker you will need Python 3.11, older versions will not work
- Is recommended to install behind a reverse proxy like Nginx for custom routing and domain names.
- Third-Party plugins may require additional configs to be set

## Selecting A Database
First you will need to decide which database to use:

- SQLite
- MySQL

If you only have a small amount of users and have no experience, its best to stick with SQLite.


## Getting Ready
There are several ways of installing Web Portal. The recommended method is through the official Docker image.

### With Docker (Recommended)
Now we can configure web-portal. We can do this using Docker Compose. So we will need to create a compose file.

This file should be placed in a directory where you are going to store all your app data. The following is an example of your directory layout:

```
web_portal/
    docker-compose.yml
    data/
    plugins/
```

### Example Compose File
This is an example config (using SQLite) which you can copy, as long as `SECRET_KEY` value is changed for security.

> Config values explained in "Configuration" section

```yaml
version: "3"

services:
  web-portal:
    container_name: web-portal
    image: ghcr.io/enchant97/web-portal:2
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      # Uncomment if you want custom plugins
      # - ./plugins:/app/plugins
    ports:
      # Change only left side
      - 8000:8000
    environment:
      # This config is built into the Docker image
      # - "DATA_PATH=/app/data"
      - "DB_URI=sqlite:///app/data/db.sqlite"
      # This must be secure
      - "SECRET_KEY=replace_me_123"
```

### Without Docker
While this is not the recommended method, it is possible and perfectly fine to run Web Portal without Docker.

> Commands shown will assume a GNU/Linux based system is being used

> Config values explained in "Configuration" section


```bash
#!/usr/bin/env bash
export WEB_PORTAL_VERSION=2.3.0
#
# Setup Environment
#
mkdir web-portal

cd web-portal

mkdir -p data
mkdir -p plugins

#
# Install/Update App
#
rm -rf .venv

python -m venv .venv

source .venv/bin/activate

git clone --depth=1 --branch=v${WEB_PORTAL_VERSION} https://github.com/enchant97/web-portal.git app-src

python -m pip install ./app-src

#
# Get Default Plugins
#
rsync -a app-src/plugins/ plugins

#
# Cleanup
#
rm -rf app-src
```

```bash
# filepath: web-portal/.env

PLUGINS_PATH="./plugins"
DATA_PATH="./data"
DB_URI="sqlite://data/db.sqlite"
SECRET_KEY="replace_me_123"
```


## Configuration
All configs shown here should be given as environment variables, or in a `.env` file.

#### Base App

| Name                  | Description                                 | Default              |
| :-------------------- | :------------------------------------------ | :------------------- |
| DB_URI                | URI of where db is stored                   |                      |
| PLUGINS_PATH          | Where plugins are stored                    |                      |
| DATA_PATH             | Where app data will be stored               |                      |
| SECRET_KEY            | Your app secret (use something secure)      | (randomly generated) |
| SECURE_COOKIES        | Whether to require https for cookies        | False                |
| LOG_LEVEL             | What log level to use                       | "INFO"               |
| SHOW_VERSION_NUMBER   | Whether the app version number is displayed | True                 |
| DISABLE_PLUGIN_LOADER | Disable the plugin loader                   | False                |
| PLUGIN_SKIP_LIST      | Skip loading specific plugins               | -                    |

> SECRET_KEY should be set, otherwise logins will be reset on server restart

> Lists must be given in JSON format e.g. `["core", "core_extras"]` or `["core_extras"]`

This table shows how the `DB_URI` values should look:

| Database | URI Format                              |
| :------- | :-------------------------------------- |
| MySQL    | mysql://user:password@hostname/database |
| SQLite   | sqlite://path-to-database.db            |

#### Core Plugin
If you have the "core" plugin installed, which comes built-in to Web Portal unless you have removed it. These are the configs:

| Name               | Description                                        | Default |
| :----------------- | :------------------------------------------------- | :------ |
| ALLOW_ICON_UPLOADS | Whether to allow icon uploads                      | True    |
| OPEN_TO_NEW_TAB    | Whether to open the link widget links in a new tab | True    |

#### Docker Specific

Other configs related to when running through the official docker image:

| Name      | Description                           | Default |
| :-------- | :------------------------------------ | :------ |
| WORKERS   | Number of separate processes to spawn | 1       |
| CERT_FILE | SSL certificate file path (public)    | -       |
| KEY_FILE  | SSL key file path (private)           | -       |

> Default values indicated with '-' are not required

> If you want HTTPS, both `CERT_FILE` and `KEY_FILE` environment values must be provided to valid certificates


## Run
Now configurations have been done, you can move on to running Web Portal for the first time.

### With Docker (Recommended)
Inside the app directory, run these commands

> Running `docker compose pull` ensures you have the latest specified in the compose file

> The `-d` argument runs the app in the background

```
docker compose pull
docker compose up -d
```

### Without Docker
After following the "Getting Ready" section, you can launch the app using Hypercorn.

> You may want to run this command through systemd or similar, this will allow the app to run in the background and startup automatically.

```bash
#!/usr/bin/env bash
source .venv/bin/activate
hypercorn 'web_portal.main:create_app()' --bind 0.0.0.0:8000 --workers 1
```

If you wish to configure Hypercorn the documentation can be found [here](https://pgjones.gitlab.io/hypercorn/), you could for example configure https or different bind methods.


## Once Running
After the app is launched, navigate in the browser to the hostname and port you configured. From there you should see a setup wizard which will guide you through the rest of the install. After you have completed this you may want to read the usage guide [here](usage.md).

If you have a question, you can ask in the GitHub discussions page at: <https://github.com/enchant97/web-portal/discussions>.
