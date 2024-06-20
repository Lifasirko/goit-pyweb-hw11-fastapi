from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from src.config import settings
from src.database.db import get_db
from src.repository import users as repository_users


class Auth:
    """
    Клас для аутентифікації та авторизації користувачів.

    Attributes:
        pwd_context (CryptContext): Контекст для хешування паролів.
        SECRET_KEY (str): Секретний ключ для підпису JWT.
        ALGORITHM (str): Алгоритм для підпису JWT.
        oauth2_scheme (OAuth2PasswordBearer): Схема для OAuth2.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "secret_key"
    ALGORITHM = "HS256"
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Перевіряє відповідність пароля його хешу.

        Args:
            plain_password (str): Пароль у відкритому вигляді.
            hashed_password (str): Хеш пароля.

        Returns:
            bool: True, якщо пароль відповідає хешу, False в іншому випадку.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Генерує хеш пароля.

        Args:
            password (str): Пароль у відкритому вигляді.

        Returns:
            str: Хеш пароля.
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Генерує новий токен доступу.

        Args:
            data (dict): Дані для токену.
            expires_delta (Optional[float]): Час життя токену в секундах.

        Returns:
            str: Згенерований токен доступу.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Генерує новий токен оновлення.

        Args:
            data (dict): Дані для токену.
            expires_delta (Optional[float]): Час життя токену в секундах.

        Returns:
            str: Згенерований токен оновлення.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        Декодує токен оновлення та повертає електронну пошту користувача.

        Args:
            refresh_token (str): Токен оновлення.

        Returns:
            str: Електронна пошта користувача.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Отримує поточного авторизованого користувача за токеном доступу.

        Args:
            token (str): Токен доступу.
            db (Session): Сеанс бази даних.

        Returns:
            User: Поточний користувач.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    def create_email_token(self, data: dict) -> str:
        """
        Генерує токен для підтвердження електронної пошти.

        Args:
            data (dict): Дані для токену.

        Returns:
            str: Згенерований токен.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str) -> str:
        """
        Отримує електронну пошту з токену.

        Args:
            token (str): Токен.

        Returns:
            str: Електронна пошта користувача.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")

    def create_reset_password_token(self, data: dict) -> str:
        """
        Генерує токен для скидання пароля.

        Args:
            data (dict): Дані для токену.

        Returns:
            str: Згенерований токен.
        """
        to_encode = data.copy()
        expire = timedelta(minutes=settings.reset_password_token_expire_minutes)
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def verify_reset_password_token(self, token: str) -> str:
        """
        Перевіряє токен для скидання пароля та повертає електронну пошту користувача.

        Args:
            token (str): Токен для скидання пароля.

        Returns:
            str: Електронна пошта користувача.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail="Invalid email")
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
