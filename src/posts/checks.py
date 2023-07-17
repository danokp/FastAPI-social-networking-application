from fastapi import HTTPException, status
from sqlalchemy import select, insert, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Post, User, user_post
from src.posts.schemas import ModelStatus404, ModelStatus403


async def check_post_existence(post_id: int, session: AsyncSession):
    '''Check if post with post_id exists.
     Raises 404 error if False or returns Post object if True.'''

    post = await session.get(Post, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ModelStatus404().model_dump(),
        )
    return post


async def check_access_to_post_changing(post: Post, user: User):
    '''Check if current user have access to change (update/delete) post.
     Raises 403 error if False.'''

    if post.creator != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ModelStatus403().model_dump(),
        )


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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ModelStatus403(
                details=f'Creator is not allowed to {reaction_type} their posts'
            ).model_dump(),
        )

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


async def post_reaction_count(
    reaction_type: str,
    session: AsyncSession,
    post_id: int,
):
    query = select(func.count(user_post.c.id)).where(and_(
        user_post.c.post_id == post_id,
        user_post.c.reaction == reaction_type,
    ))
    reaction_count = await session.execute(query)
    return {f'{reaction_type}_count': reaction_count.scalar()}
