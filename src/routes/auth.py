from fastapi import Depends, HTTPException, status, APIRouter, Security, BackgroundTasks, Request
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas import UserResponse, UserModel, TokenModel, RequestEmail, ResetPassword
from src.services.auth import auth_service
from src.services.email import send_email, send_reset_password_email

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request,
                 db: AsyncSession = Depends(get_db)):
    """
    Реєструє нового користувача.

    Args:
        body (UserModel): Дані нового користувача.
        background_tasks (BackgroundTasks): Завдання для виконання у фоновому режимі.
        request (Request): HTTP запит.
        db (AsyncSession): Сеанс бази даних.

    Returns:
        dict: Дані нового користувача та повідомлення про успішну реєстрацію.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Авторизація користувача.

    Args:
        body (OAuth2PasswordRequestForm): Дані для авторизації (email та пароль).
        db (AsyncSession): Сеанс бази даних.

    Returns:
        TokenModel: Токени доступу та оновлення.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: AsyncSession = Depends(get_db)):
    """
    Оновлення токена доступу за допомогою токену оновлення.

    Args:
        credentials (HTTPAuthorizationCredentials): Авторизаційні дані.
        db (AsyncSession): Сеанс бази даних.

    Returns:
        TokenModel: Нові токени доступу та оновлення.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Підтвердження електронної пошти користувача.

    Args:
        token (str): Токен для підтвердження.
        db (AsyncSession): Сеанс бази даних.

    Returns:
        dict: Повідомлення про результат підтвердження.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    Запит на повторне відправлення електронного листа для підтвердження.

    Args:
        body (RequestEmail): Дані для повторного відправлення.
        background_tasks (BackgroundTasks): Завдання для виконання у фоновому режимі.
        request (Request): HTTP запит.
        db (AsyncSession): Сеанс бази даних.

    Returns:
        dict: Повідомлення про результат запиту.
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.post("/request-reset-password")
async def request_reset_password(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                                 db: Session = Depends(get_db)):
    """
    Запит на відновлення пароля.

    Args:
        body (RequestEmail): Дані для відновлення пароля.
        background_tasks (BackgroundTasks): Завдання для виконання у фоновому режимі.
        request (Request): HTTP запит.
        db (Session): Сеанс бази даних.

    Returns:
        dict: Повідомлення про результат запиту.
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    reset_token = auth_service.create_reset_password_token(data={"sub": user.email})
    reset_url = f"{request.base_url}api/auth/reset-password?token={reset_token}"
    background_tasks.add_task(send_reset_password_email, user.email, reset_url)
    return {"message": "Password reset email has been sent."}


@router.post("/reset-password")
async def reset_password(body: ResetPassword, db: Session = Depends(get_db)):
    """
    Скидання пароля користувача.

    Args:
        body (ResetPassword): Новий пароль та токен для відновлення.
        db (Session): Сеанс бази даних.

    Returns:
        dict: Повідомлення про успішне скидання пароля.
    """
    email = await auth_service.verify_reset_password_token(body.token)
    user = await repository_users.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password = auth_service.get_password_hash(body.password)
    db.commit()
    return {"message": "Password has been reset successfully."}
