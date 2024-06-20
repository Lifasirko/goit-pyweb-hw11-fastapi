from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime


class ContactBase(BaseModel):
    """
    Базова схема для контактів.

    Attributes:
        first_name (str): Ім'я контакту.
        last_name (str): Прізвище контакту.
        email (EmailStr): Електронна пошта контакту.
        phone_number (str): Номер телефону контакту.
        birthday (Optional[date]): Дата народження контакту.
        additional_info (Optional[str]): Додаткова інформація про контакт.
        id (Optional[str]): Ідентифікатор контакту.
        created_at (Optional[str]): Дата створення контакту.
    """
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: Optional[date] = None
    additional_info: Optional[str] = None
    id: Optional[str] = None
    created_at: Optional[str] = None


class ContactCreate(ContactBase):
    """
    Схема для створення нового контакту.
    """
    pass


class ContactUpdate(ContactBase):
    """
    Схема для оновлення контакту.
    """
    pass


class Contact(ContactBase):
    """
    Схема контакту з обов'язковим ідентифікатором.
    """
    id: int

    class Config:
        from_attributes = True


class ContactResponse(ContactBase):
    """
    Схема для відповіді на запити про контакт.

    Attributes:
        id (int): Ідентифікатор контакту.
        created_at (datetime): Дата створення контакту.
    """
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserModel(BaseModel):
    """
    Схема для створення нового користувача.

    Attributes:
        username (str): Ім'я користувача.
        email (EmailStr): Електронна пошта користувача.
        password (str): Пароль користувача.
    """
    username: str = Field(min_length=5, max_length=16)
    email: EmailStr
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    """
    Схема для даних користувача в базі даних.

    Attributes:
        id (int): Ідентифікатор користувача.
        username (str): Ім'я користувача.
        email (EmailStr): Електронна пошта користувача.
        created_at (datetime): Дата створення користувача.
        avatar (Optional[str]): URL аватара користувача.
    """
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """
    Схема для відповіді на запити про користувача.

    Attributes:
        user (UserDb): Дані користувача.
        detail (str): Повідомлення про успішне створення користувача.
    """
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
    Схема для токенів аутентифікації.

    Attributes:
        access_token (str): Токен доступу.
        refresh_token (str): Токен оновлення.
        token_type (str): Тип токену.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    Схема для запиту на відправлення електронного листа.

    Attributes:
        email (EmailStr): Електронна пошта користувача.
    """
    email: EmailStr


class ResetPassword(BaseModel):
    """
    Схема для скидання пароля.

    Attributes:
        token (str): Токен для скидання пароля.
        password (str): Новий пароль користувача.
    """
    token: str
    password: str
