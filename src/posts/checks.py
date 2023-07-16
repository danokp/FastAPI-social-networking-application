from fastapi import HTTPException
from sqlalchemy import select, insert, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Post, User, user_post


async def check_post_existence(post_id: int, session: AsyncSession):
    '''Check if post with post_id exists.
     Raises error if False or returns Post object if True.'''

    post = await session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail={
            'status': 'error',
            'data': None,
            'details': 'No Post with such id',
        })
    return post


async def check_access_to_post_changing(post: Post, user: User):
    '''Check if current user have access to change (update/delete) post.
     Raises error if False.'''

    if post.creator != user.id:
        raise HTTPException(status_code=403, detail={
            'status': 'error',
            'data': None,
            'details': 'Only creator of the post can update it',
        })


async def rate_post(
    post_id: int,
    session: AsyncSession,
    user: User,
    reaction_type: str,
):
    '''Rate (like or dislike) post.'''
    exact_post = await check_post_existence(post_id, session)

    if exact_post.creator == user.id:
        print('error')
        raise HTTPException(status_code=403, detail={
            'status': 'error',
            'data': None,
            'details': f'Creator is not allowed to {reaction_type} their posts'
        })

    query = select(user_post).where(and_(
        user_post.c.user_id == user.id,
        user_post.c.post_id == post_id,
    ))
    post_reaction_lst = await session.execute(query)
    post_reaction = post_reaction_lst.first()
    if post_reaction is None:
        stmt = insert(user_post).values(
            user_id=user.id,
            post_id=post_id,
            reaction=reaction_type
        )
    else:
        reaction = None if post_reaction.reaction == reaction_type else reaction_type
        stmt = update(user_post). \
            where(user_post.c.id == post_reaction.id). \
            values(reaction=reaction)

    await session.execute(stmt)
    await session.commit()
    return {
        'status': 'success',
        'data': None,
        'details': f'Post {post_id} is {reaction_type}d',
    }
