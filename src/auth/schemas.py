from fastapi_users import schemas
from pydantic import ConfigDict


class UserRead(schemas.BaseUser[int]):
    nick_name: str
    first_name: str
    last_name: str
    model_config = ConfigDict(from_attributes=True)



class UserCreate(schemas.BaseUserCreate):
    nick_name: str
    first_name: str
    last_name: str

#
# class UserUpdate(schemas.BaseUserUpdate):
#     pass
