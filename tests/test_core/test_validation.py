from copy import deepcopy

from web_portal.core.constants import PUBLIC_ACCOUNT_USERNAME
from web_portal.core.validation import check_password, is_username_allowed


class TestCheckPassword:
    _username = "user"
    _valid_pw = "akgGG308"

    def test_valid_without_confirm(self):
        assert check_password(self._username, self._valid_pw) is None

    def test_valid_with_confirm(self):
        test_pw_conf = deepcopy(self._valid_pw)
        assert check_password(self._username, self._valid_pw, test_pw_conf) is None

    def test_invalid_min_length(self):
        assert check_password(self._username, self._valid_pw[:5]) is not None

    def test_invalid_max_length(self):
        assert check_password(self._username, self._valid_pw * 1800) is not None

    def test_invalid_username_lower(self):
        assert check_password(self._username, self._username + self._valid_pw) is not None

    def test_invalid_username_upper(self):
        assert check_password(self._username, self._username.upper() + self._valid_pw) is not None

    def test_invalid_with_confirm(self):
        assert check_password(self._username, self._valid_pw, self._valid_pw[:5] * 2) is not None


class TestIsUsernameAllowed:
    def test_valid_lowercase(self):
        assert is_username_allowed("leo")

    def test_valid_numbers(self):
        assert is_username_allowed("user23")

    def test_valid_uppercase(self):
        assert is_username_allowed("Steve")

    def test_invalid_characters(self):
        assert not is_username_allowed("user-1")

    def test_invalid_length(self):
        assert not is_username_allowed("user" * 200)

    def test_invalid_restricted(self):
        assert not is_username_allowed(deepcopy(PUBLIC_ACCOUNT_USERNAME))
