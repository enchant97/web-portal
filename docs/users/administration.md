# Administration
This section will guide administrators in the behind-the-scenes configuration.

## Recover User Accounts
If you are unable to change a user password via the UI, you can set a new one in the directly in the database.

1. Generate a hashed password using the `hash_password.py` script.
2. Update the database field in `user.password_hash` to the password hash

Example SQL:

```sql
UPDATE user SET password_hash = 'THE-PASSWORD-HASH' WHERE username = 'THE-USERNAME';
```


## Plugins
Web Portal works by implementing a plugin system allowing for different widgets to be installed.

Plugins are stored in a plugins folder, this plugin system allows you to easily install a new plugin (or remove) without requiring Web Portal to be re-installed.

### Add
To install a plugin into this folder follow these steps:

1. Ensure Web Portal is shutdown
2. Ensure plugin loader is enabled (set by the environment variable)
3. Ensure "plugins" directory has a empty file called `__init__.py` in it.
4. Copy/Move plugin package into folder
5. Startup Web Portal
6. Plugin should now be registered

### Remove
To remove follow these steps:

1. Follow any steps given by the plugins guide
2. Ensure Web Portal is shutdown
3. Move/Delete the specific plugin package from the "plugins" directory
4. Startup Web Portal
5. Go to `"Plugin Settings" > "Missing Plugins"` (as admin) to remove plugin data

### Where Is The Plugins Directory?
Assuming you are running the official Docker image; Web Portal is structured as shown below:

```
data/
    ...

app/
    web_portal/
        ...

    plugins/
        core
        core_extras
        another_plugin
        ...
```

To add plugins you can mount a volume as shown below using Docker Compose:

```yml
# filepath: docker-compose.yml
volumes:
  - ./data:/app/data
  - ./plugins:/app/plugins
```

> IMPORTANT: When you mount the plugins folder as a docker volume it will disable the built-in plugins provided by the image.
