"""
Module to provide validation functions for forms/requests
"""

import re

VALID_USERNAME_RE = r"^[a-zA-Z0-9]+$"


def is_username_allowed(username: str) -> bool:
    if (len(username) > 0 and len(username) <= 20) and \
            re.fullmatch(VALID_USERNAME_RE, username) is not None:
        return True
    return False
