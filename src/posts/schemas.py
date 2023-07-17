from datetime import datetime
from types import NoneType

from pydantic import BaseModel

from src.models import User


class PostCreate(BaseModel):
    name: str
    description: str


class PostUpdate(BaseModel):
    name: str
    description: str


class PostRead(BaseModel):
    id: int
    name: str
    description: str
    creator: str
    created_at: datetime
    like_count: int
    dislike_count: int


class ModelStatus(BaseModel):
    status: str = 'error'
    data: NoneType = None
    details: str


class ModelStatus404(ModelStatus):
    details: str = 'No Post with such id'


class ModelStatus403(ModelStatus):
    details: str = 'Only creator of the post can change it'


class ModelStatus500(ModelStatus):
    details: str = 'Something went wrong on Internal Server'


class ModelStatus200(ModelStatus):
    status: str = 'success'


class ModelStatus200PostRead(ModelStatus200):
    data: PostRead


class ModelStatus200PostUpdate(ModelStatus200):
    data: PostUpdate
    details: str = 'Post has been updated successfully.'


class ModelStatus200PostCreate(ModelStatus200):
    data: PostCreate
    details: str = 'Post has been created successfully.'


class ModelStatus200PostDelete(ModelStatus200):
    details: str = 'Post has been deleted successfully.'


class ModelStatus200LikeDislike(ModelStatus200):
    details: str = 'Post 0 is liked/disliked'

class ModelStatus404LikeDislike(ModelStatus):
    details: str = 'Creator is not allowed to like/dislike their posts'
