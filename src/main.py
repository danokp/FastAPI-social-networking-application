from fastapi import FastAPI

from .auth.auth_config import fastapi_users, auth_backend
from .auth.schemas import UserRead, UserCreate
from .posts.router import router as post_router


app = FastAPI(
    title='Social network',
    debug=True,
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(post_router)
