PUBLIC_ACCOUNT_USERNAME = "public"

VALID_USERNAME_RE = r"^[a-zA-Z0-9]+$"
MAX_USERNAME_LENGTH = 128

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 1024


class SystemSettingKeys:
    """
    Collection of all system setting keys for base app
    """
    PORTAL_SECURED = "PORTAL_SECURED"
    SHOW_WIDGET_HEADERS = "SHOW_WIDGET_HEADERS"
    DEMO_MODE = "DEMO_MODE"
    HAS_SETUP = "has_setup"
