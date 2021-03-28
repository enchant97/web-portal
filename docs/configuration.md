# Configuration

[Home](index.md)

    You can configure the app using a .env file or through environment variables.

## Config Options
| Name                  | Description                                   | Required | Default            |
|:----------------------|:----------------------------------------------|:---------|:-------------------|
| DB_URL                | URI of where db is stored                     | YES      |                    |
| SECRET_KEY            | Your app secret (use something secure)        | YES      |                    |
| ADMIN_CREATE_OVERRIDE | Create a new admin account even if one exists | NO       | False              |
| UNSECURE_LOGIN        | Whether to allow http for cookies             | NO       | False              |
| PORTAL_SECURED        | Whether the portal requires a login           | NO       | False              |
| SHOW_PANEL_HEADERS    | Show the panel header names                   | NO       | True               |
| LOG_LEVEL             | What log level to use                         | NO       | "INFO"             |
| HOST                  | host to listen for requests                   | NO       | "127.0.0.1"        |
| PORT                  | port to listen for requests                   | NO       | 8000               |
| BASE_URL              | The base url prefix                           | NO       | "/"                |
