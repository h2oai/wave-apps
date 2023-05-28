"""Demonstrator for authentication with h2o wave and JWT.

Replace print statements with logging of your choice or drop them completely.
"""
from datetime import datetime, timedelta
from typing import Callable, Any, Awaitable

from h2o_wave import Q, ui, on, handle_on

from jose import JWTError, jwt
from passlib.context import CryptContext

from mongodb_layer import get_hashed_pw, has_user  # Use whatever database layer to query this data
from util import add_card, clear_cards


# Create with openssl rand -hex 32
# TODO: Replace with your own secret key!!!!
SECRET_KEY = "e662a467b5d75f28652d0cd110505164db8ef412cfbd15a9bce1e5b2425edd3f"
ALGORITHM = "HS256"
# Arbitrary timeout
ACCESS_TOKEN_EXPIRE_MINUTES = 120

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def check_secret(q: Q):
    """Validate the secret.

    This should check the JWT on authenticity and timestamp validity.
    """
    if q.user.secret is None:
        return False
    try:
        payload = jwt.decode(q.user.secret, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload["user"]
        if payload["expires"] is not None:
            expires = datetime.fromisoformat(payload["expires"])
        else:
            expires = None
        print(f"Username: {username} | expires: {expires}")
    except JWTError:
        print("Could not validate credentials")
        return False
    else:
        if not has_user(username):
            print("Unknown user")
            return False
        if expires is not None and expires < datetime.utcnow():
            print("Token expired")
            return False
    return True


def get_password_hash(password: str):
    """Hash the password. Used to register a user"""
    return pwd_context.hash(password)


def get_secret(user: str, password: str, stay_logged_in: bool = False):
    """Validate credentials and return secret.

    This should safely validate the credentials against a data storage.
    If valid, create a JWT and return
    """
    hashed_pw = get_hashed_pw(user)
    if hashed_pw is None:
        print("No credentials found for user")
        return None

    if pwd_context.verify(password, hashed_pw):
        if stay_logged_in:
            expire = None
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            expire = expire.isoformat()
        to_encode = {"user": user, "expires": expire}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    else:
        print("Password invalid")
        return None


async def handle_auth_on(q: Q, home_page: Callable[[Q], Awaitable[Any]]):
    """Wrap default handle on with a secret check.

    Only handle routing if secret is valid. After successful login, loads home_page.
    """
    if not check_secret(q):
        if q.args.login:
            await login(q, home_page=home_page)
        else:
            # Display login page for invalid secret
            await login_page(q)
    else:
        if q.client.new:
            # Load header and sidebar on first client connection
            make_header_and_sidebar(q)
            q.client.new = False
        if q.args.logout:
            await logout(q)
        else:
            await handle_on(q)


def make_header_and_sidebar(q: Q):
    """Populate header and sidebar

    Header and sidebar should only be visible when user is logged in."""
    q.page["header"].items = [ui.menu([
        ui.command(name="#profile", icon="Contact", label="Profile"),
        ui.command(name='logout', icon="Leave", label='Logout'),
    ])]

    q.page['sidebar'].items = [
        ui.nav_group('Menu', items=[
            ui.nav_item(name='#page1', label='Home'),
            ui.nav_item(name='#page2', label='Charts'),
            ui.nav_item(name='#page3', label='Grid'),
            ui.nav_item(name='#page4', label='Form'),
        ]),
    ]


def clear_header_and_sidebar(q: Q):
    """Remove header and sidebar

    Header and sidebar should only be visible when user is logged in."""
    q.page["header"].items = []
    q.page["header"].secondary_items = []
    q.page["sidebar"].items = []


@on()
async def login_page(q: Q, err_msg: str = ""):
    """Login page.

    If the user is not logged in, any path of the app should lead here.
    """
    clear_cards(q)
    items = [
        ui.textbox('username', 'User'),
        ui.textbox('password', 'Password', password=True),
        ui.checkbox('stay_logged_in', label="Remember me", tooltip="Login does not expire."),
        ui.button('login', "Login", primary=True)
    ]
    if err_msg:
        items.append(ui.text_m(err_msg))
    add_card(q, 'login', ui.form_card(box='centered', items=items))


@on()
async def login(q: Q, home_page: Callable[[Q], Awaitable[Any]]):
    """Process login.

    Return to login page if credentials are invalid. Otherwise, route to home page.
    """
    print("processing login")
    if q.args.username == "" or q.args.password == "":
        await login_page(q, "Missing username or password")
    else:
        secret = get_secret(q.args.username, q.args.password, q.args.stay_logged_in)
        if secret is not None:
            q.user.secret = secret
            q.user.username = q.args.username
            make_header_and_sidebar(q)
            print("awaiting home page")
            await home_page(q)
        else:
            await login_page(q, "Wrong credentials")


@on()
async def logout(q: Q):
    """Remove the secret. Remove header and sidebar"""
    q.user.secret = None
    clear_header_and_sidebar(q)
    await login_page(q)
