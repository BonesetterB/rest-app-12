from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.model import User
from src.schemas import UserSchema,UserResponseSchema



async def get_user_by_email(email: str, db: AsyncSession) -> User:
    """
    Fiend user.

    :param email: The email fot fiend user.
    :type email: str
    :param db: The database session.
    :type db: AsyncSession
    :return: Return user.
    :rtype: User
    """

    sq = select(User).filter(User.email == email)
    result = await db.execute(sq)
    user =  result.scalar()
    return user

async def user_to_response_schema(user: User) -> UserResponseSchema:
    """
    Changes type of user

    :param user: The user.
    :type user: User
    :return: Return user in type UserResponseSchema .
    :rtype: UserResponseSchema
    """
    return UserResponseSchema(
        id=user.id,
        username=user.username,
        email=user.email,
        avatar=user.avatar
    )

async def create_user(body: UserSchema, db: AsyncSession) -> User:
    """
    Created User.

    :param body: Body user.
    :type body: UserSchema
    :param db: The database session.
    :type db: AsyncSession
    :return: Return new user.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    user_data = body.model_dump()
    new_user = User(**user_data, avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    """
    Update the refresh token of a user.

    :param user: The user to update the token for.
    :type user: User
    :param token: The new refresh token.
    :type token: str | None
    :param db: The database session.
    :type db: AsyncSession
    :return: Return token.
    :rtype: str | None
    """

    user.refresh_token = token
    await db.commit()

async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Confirm a user's email.

    :param email: The email of the user to confirm.
    :type email: str
    :param db: The database session.
    :type db: AsyncSession
    :return: Confirmed user email.
    :rtype: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()

async def update_avatar(email, url: str, db: AsyncSession) -> User:
    """
    Update a user's avatar.

    :param email: The email of the user to update the avatar for.
    :type email: str
    :param url: The new avatar URL.
    :type url: str
    :param db: The database session.
    :type db: AsyncSession
    :return: The updated user.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    return user