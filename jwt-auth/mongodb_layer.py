"""Basic mongodb interface to store and retrieve user credentials"""
from mongoengine import connect
from mongoengine import Document, StringField, errors

connection = connect(db="wave-app", host="localhost", port=27017)


class Credentials(Document):
    user = StringField(required=True, unique=True)
    hashed_pw = StringField(required=True)


def create_user(user: str, hashed_pw: str):
    new_user = Credentials(user=user, hashed_pw=hashed_pw)
    try:
        new_user.save()
    except (errors.ValidationError, errors.OperationError) as e:
        print(e)
        return False
    return True


def has_user(user: str):
    user_obj = Credentials.objects(user=user)
    return len(user_obj) != 0


def get_hashed_pw(user: str):
    user_obj = Credentials.objects(user=user)
    if len(user_obj) == 0:
        print("Could not find user", user)
    elif len(user_obj) > 1:
        print("More than 1 user found:", user)
    else:
        return user_obj[0].hashed_pw
    return None
