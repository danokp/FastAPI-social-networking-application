from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Column, Integer, TIMESTAMP, String, ForeignKey
from sqlalchemy import MetaData, Table
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types.choice import ChoiceType

from src.database import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    '''User model'''

    metadata = MetaData()

    id = Column(Integer, primary_key=True)
    nick_name = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)


class Post(Base):
    '''Post model'''

    __tablename__ = "post"

    metadata = MetaData()

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    creator = Column(Integer, ForeignKey(User.id))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


REACTIONS = [
    ('like', 'Like'),
    ('dislike', 'Dislike'),
]

user_post = Table(
    'user_post',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey(User.id)),
    Column('post_id', Integer, ForeignKey(Post.id)),
    Column('reaction', ChoiceType(REACTIONS), nullable=True),
)
