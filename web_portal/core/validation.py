"""
Module to provide validation functions for forms/requests
"""
import re

from .constants import (MAX_PASSWORD_LENGTH, MAX_USERNAME_LENGTH,
                        MIN_PASSWORD_LENGTH, PUBLIC_ACCOUNT_USERNAME,
                        VALID_USERNAME_RE)


def check_password(
        username: str,
        password: str,
        password_conf: str | None = None) -> str | None:
    if password_conf is not None and password != password_conf:
        return "passwords do not match"
    elif username.lower() in password.lower():
        return "password contains username"
    elif len(password) < MIN_PASSWORD_LENGTH:
        return f"password is too short, must be at least {MIN_PASSWORD_LENGTH} characters"
    elif len(password) > MAX_PASSWORD_LENGTH:
        return "password is too long"


def is_username_allowed(username: str) -> bool:
    if username == PUBLIC_ACCOUNT_USERNAME:
        return False
    if (len(username) > 0 and len(username) <= MAX_USERNAME_LENGTH) and \
            re.fullmatch(VALID_USERNAME_RE, username) is not None:
        return True
    return False
