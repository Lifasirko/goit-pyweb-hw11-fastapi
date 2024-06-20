from sqlalchemy import Column, Integer, String, Date, Text, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship

# from sqlalchemy.ext.declarative import declarative_base # Оновлення алхімії
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Contact(Base):
    """
    Модель для зберігання контактів.

    Attributes:
        id (int): Унікальний ідентифікатор контакту.
        first_name (str): Ім'я контакту.
        last_name (str): Прізвище контакту.
        email (str): Електронна пошта контакту.
        phone_number (str): Номер телефону контакту.
        birthday (date): Дата народження контакту.
        additional_info (str): Додаткова інформація про контакт.
        user_id (int): Ідентифікатор користувача, до якого належить контакт.
        user (User): Відношення до користувача.
        created_at (datetime): Дата та час створення контакту.
    """
    __tablename__ = 'contacts'

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    birthday = Column(Date)
    additional_info = Column(Text)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="notes")
    created_at = Column(DateTime, default=func.now())


class User(Base):
    """
    Модель для зберігання користувачів.

    Attributes:
        id (int): Унікальний ідентифікатор користувача.
        username (str): Ім'я користувача.
        email (str): Електронна пошта користувача.
        password (str): Пароль користувача.
        created_at (datetime): Дата та час створення користувача.
        avatar (str): URL до аватара користувача.
        refresh_token (str): Токен оновлення для користувача.
        confirmed (bool): Стан підтвердження облікового запису.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('crated_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
