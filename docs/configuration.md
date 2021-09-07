# Configuration

[Home](index.md)

    You can configure the app using a .env file or through environment variables.

## Config Options
| Name                  | Description                                   | Required | Default            | Docker Only |
|:----------------------|:----------------------------------------------|:---------|:-------------------|:------------|
| DB_URI                | URI of where db is stored                     | YES      |                    | No          |
| SECRET_KEY            | Your app secret (use something secure)        | YES      |                    | No          |
| ADMIN_CREATE_OVERRIDE | Create a new admin account even if one exists | NO       | False              | No          |
| UNSECURE_LOGIN        | Whether to allow http for cookies             | NO       | False              | No          |
| PORTAL_SECURED        | Whether the portal requires a login           | NO       | False              | No          |
| SHOW_PANEL_HEADERS    | Show the panel header names                   | NO       | True               | No          |
| LOG_LEVEL             | What log level to use                         | NO       | "INFO"             | No          |
| HOST                  | Host to listen for requests                   | NO       | "0.0.0.0"          | Yes         |
| PORT                  | Port to listen for requests                   | NO       | 8000               | Yes         |
| WORKERS               | Number of seperate processes to spawn         | NO       | 1                  | Yes         |