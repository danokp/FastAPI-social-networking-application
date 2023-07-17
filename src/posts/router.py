from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.database import get_async_session
from src.models import Post, User, user_post
from src.posts.schemas import (PostCreate, PostUpdate, ModelStatus404,
                               ModelStatus500, ModelStatus403,
                               ModelStatus200PostRead,
                               ModelStatus200PostUpdate,
                               ModelStatus200PostCreate, ModelStatus200,
                               ModelStatus200PostDelete,
                               ModelStatus200LikeDislike,
                               ModelStatus404LikeDislike)
from src.auth.auth_config import current_user
from src.posts.checks import (
    check_post_existence,
    check_access_to_post_changing,
    rate_post,
    post_reaction_count,
)


router = APIRouter(
    prefix='/posts',
    tags=['Posts'],
)


@router.get('/', responses={
    200: {'model': ModelStatus200PostRead},
    500: {'model': ModelStatus500},
})
async def get_post_list(
    session: AsyncSession = Depends(get_async_session),
):
    '''Get list of all posts'''

    try:
        query = select(Post)
        result = await session.execute(query)
        post_list = []
        for post in result.scalars():
            like_count = await post_reaction_count(
                'like',
                session,
                post.id,
            )
            dislike_count = await post_reaction_count(
                'dislike',
                session,
                post.id,
            )
            post_list.append(post.__dict__ | like_count | dislike_count)

        return {
            'status': 'success',
            'data': post_list,
            'details': None,
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=ModelStatus500().model_dump(),
        )


@router.post('/', responses={
    200: {'model': ModelStatus200PostCreate},
    500: {'model': ModelStatus500},
})
async def create_post(
    new_post: PostCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    '''Create a new post'''

    try:
        stmt = insert(Post).values(**new_post.model_dump(), creator=user.id)
        await session.execute(stmt)
        await session.commit()
        return {
            'status': 'success',
            'data': new_post.model_dump(),
            'details': 'Post has been created successfully.',
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=ModelStatus500().model_dump(),
        )


@router.get('/{post_id}', responses={
    200: {'model': ModelStatus200PostRead},
    404: {'model': ModelStatus404},
    500: {'model': ModelStatus500},
})
async def get_post(
    post_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    '''Get one specific post by id.'''

    try:
        exact_post = await check_post_existence(post_id, session)
        like_count = await post_reaction_count('like', session, post_id)
        dislike_count = await post_reaction_count('dislike', session, post_id)

        return {
            'status': 'success',
            'data': exact_post.__dict__ | like_count | dislike_count,
            'details': None,
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=ModelStatus500().model_dump(),
        )


@router.delete('/{post_id}', responses={
    200: {'model': ModelStatus200PostDelete},
    403: {'model': ModelStatus403},
    404: {'model': ModelStatus404},
    500: {'model': ModelStatus500},
})
async def delete_post(
    post_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    '''Delete post by id.'''

    try:
        post_to_delete = await check_post_existence(post_id, session)
        await check_access_to_post_changing(post_to_delete, user)

        await session.delete(post_to_delete)
        await session.commit()
        return {
            'status': 'success',
            'data': None,
            'details': 'Post has been deleted successfully.',
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=ModelStatus500().model_dump(),
        )


@router.put('/{post_id}', responses={
    200: {'model': ModelStatus200PostUpdate},
    403: {'model': ModelStatus403},
    404: {'model': ModelStatus404},
    500: {'model': ModelStatus500},
})
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    '''Update post'''

    try:
        exact_post = await check_post_existence(post_id, session)
        await check_access_to_post_changing(exact_post, user)

        stmt = update(Post).\
                where(Post.id == post_id).\
                values(**post_update.model_dump())
        await session.execute(stmt)
        await session.commit()
        return {
            'status': 'success',
            'data': post_update.model_dump(),
            'details': 'Post has been updated successfully.',
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=ModelStatus500().model_dump(),
        )


@router.patch('/{post_id}/like', responses={
    200: {'model': ModelStatus200LikeDislike},
    403: {'model': ModelStatus403},
    404: {'model': ModelStatus404LikeDislike},
    500: {'model': ModelStatus500},
})
async def like_post(
    post_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    '''Like post'''

    try:
        return await rate_post(post_id, session, user, reaction_type='like')

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=ModelStatus500().model_dump(),
        )


@router.patch('/{post_id}/dislike', responses={
    200: {'model': ModelStatus200LikeDislike},
    403: {'model': ModelStatus403},
    404: {'model': ModelStatus404LikeDislike},
    500: {'model': ModelStatus500},
})
async def dislike_post(
        post_id: int,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    '''Dislike post'''

    try:
        return await rate_post(post_id, session, user, reaction_type='dislike')

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=ModelStatus500().model_dump(),
        )
