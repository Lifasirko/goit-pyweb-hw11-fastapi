from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    """
    Отримує користувача за його електронною поштою.

    Args:
        email (str): Електронна пошта користувача.
        db (AsyncSession): Сеанс бази даних.

    Returns:
        User: Користувач або None, якщо користувача не знайдено.
    """
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def create_user(body: UserModel, db: AsyncSession) -> User:
    """
    Створює нового користувача.

    Args:
        body (UserModel): Дані нового користувача.
        db (AsyncSession): Сеанс бази даних.

    Returns:
        User: Створений користувач.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    """
    Оновлює токен оновлення для користувача.

    Args:
        user (User): Користувач, для якого оновлюється токен.
        token (str | None): Новий токен оновлення або None.
        db (AsyncSession): Сеанс бази даних.
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Підтверджує електронну пошту користувача.

    Args:
        email (str): Електронна пошта користувача.
        db (AsyncSession): Сеанс бази даних.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar(email: str, url: str, db: AsyncSession) -> User:
    """
    Оновлює аватар користувача.

    Args:
        email (str): Електронна пошта користувача.
        url (str): URL нового аватара.
        db (AsyncSession): Сеанс бази даних.

    Returns:
        User: Користувач з оновленим аватаром.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
