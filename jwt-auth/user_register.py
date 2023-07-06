"""
Basic CLI script to register a new user via the wave_auth interface.
"""
from getpass import getpass

from mongodb_layer import create_user
from wave_auth import get_password_hash


if __name__ == '__main__':
    user = ""
    while user == "":
        user = input("Enter username: ")
    hash_pw = ""
    while hash_pw == "":
        hash_pw = get_password_hash(getpass("Enter password: "))

    create_user(user, hash_pw)
    print("Created user:", user)
