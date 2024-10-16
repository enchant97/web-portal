#!/bin/env python
from getpass import getpass

from werkzeug.security import generate_password_hash


def main():
    password = getpass("New Password: ")
    password_confirm = getpass("Confirm Password: ")

    if password != password_confirm:
        print("Passwords Do Not Match")

    print(generate_password_hash(password))


if __name__ == "__main__":
    main()
