# names for plugins that would cause problems with internal functions
RESTRICTED_PLUGIN_NAMES = (
    "web_portal",
    "admin",
    "install",
    "login",
    "portal",
    "settings",
    "static",
    "plugin",
)

PUBLIC_ACCOUNT_USERNAME = "public"

VALID_USERNAME_RE = r"^[a-zA-Z0-9]+$"
MAX_USERNAME_LENGTH = 128

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 1024

DEFAULT_BRANDING = {
    "title": "Portal",
}


class SystemSettingKeys:
    """
    Collection of all system setting keys for base app
    """

    PORTAL_SECURED = "PORTAL_SECURED"
    BRANDING = "BRANDING"
    DEMO_MODE = "DEMO_MODE"
    HAS_SETUP = "has_setup"
