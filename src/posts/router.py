from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import Post, User
from src.posts.schemas import PostCreate, PostRead, PostUpdate
from src.auth.auth_config import current_user
from src.posts.checks import (
    check_post_existence,
    check_access_to_post_changing,
    rate_post,
)


router = APIRouter(
    prefix='/posts',
    tags=['Posts'],
)


@router.get('/')
async def get_post_list(
    session: AsyncSession = Depends(get_async_session),
):
    '''Get list of all posts'''
    try:
        query = select(Post)
        result = await session.execute(query)
        post_list = [post for post in result.scalars()]
        return {
            'status': 'success',
            'data': post_list,
            'details': None,
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            'status': 'error',
            'data': None,
            'details': None,
        })


@router.post('/')
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
        raise HTTPException(status_code=500, detail={
            'status': 'error',
            'data': None,
            'details': None,
        })


@router.get('/{post_id}')
async def get_post(
    post_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    '''Get one specific post by id.'''

    try:
        exact_post = await check_post_existence(post_id, session)

        return {
            'status': 'success',
            'data': exact_post,
            'details': None,
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail={
            'status': 'error',
            'data': None,
            'details': None,
        })


@router.delete('/{post_id}')
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
        raise HTTPException(status_code=500, detail={
            'status': 'error',
            'data': None,
            'details': None,
        })


@router.put('/{post_id}')
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
        raise HTTPException(status_code=500, detail={
            'status': 'error',
            'data': None,
            'details': None,
        })


@router.patch('/{post_id}/like')
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
        raise HTTPException(status_code=500, detail={
            'status': 'error',
            'data': None,
            'details': None,
        })


@router.patch('/{post_id}/dislike')
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
        raise HTTPException(status_code=500, detail={
            'status': 'error',
            'data': None,
            'details': None,
        })
