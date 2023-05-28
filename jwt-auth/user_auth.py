"""
Basic CLI script to test the wave_auth backend
"""
from getpass import getpass

from wave_auth import get_secret, check_secret


class User:
    def __init__(self, secret: str):
        self.secret = secret


class QDummy:
    def __init__(self, secret: str):
        self.user = User(secret)


if __name__ == '__main__':
    user = ""
    while user == "":
        user = input("Enter username: ")
    password = ""
    while password == "":
        password = getpass("Enter password: ")
        if password == "":
            print("Error: Password may not be empty")
        if len(password) < 4:
            print("Error: Password must be at least 4 characters long")

    secret = get_secret(user, password)
    print("Got JWT:", secret)

    q_dummy = QDummy(secret)
    print("JWT valid:", check_secret(q_dummy))
