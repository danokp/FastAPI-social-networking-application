from datetime import datetime

from pydantic import BaseModel


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
