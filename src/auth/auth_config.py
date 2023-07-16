from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend, CookieTransport, JWTStrategy
)

from src.auth.manager import get_user_manager
from src.config import AUTH_SECRET_KEY
from src.models import User


cookie_transport = CookieTransport(
    cookie_name='social_network',
    cookie_max_age=3600,
)


def get_jwt_strategy() -> JWTStrategy:
    '''Define JWT strategy for token generation and secure'''

    return JWTStrategy(secret=AUTH_SECRET_KEY, lifetime_seconds=3600)


# Create authentication backend as a combination of transport and strategy.
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()
