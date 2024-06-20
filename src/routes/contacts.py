from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from src.repository.contacts import get_contacts, get_contact, get_upcoming_birthdays, cr_contact
from src.services.auth import auth_service
from src.repository import contacts as repository_contacts

from src.schemas import ContactResponse, ContactCreate, ContactUpdate

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=5, seconds=60))],
             status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Створює новий контакт для поточного користувача.

    Args:
        contact (ContactCreate): Дані для створення нового контакту.
        db (Session): Сеанс бази даних.
        current_user (User): Поточний авторизований користувач.

    Returns:
        ContactResponse: Створений контакт.
    """
    return await cr_contact(db=db, contact=contact, user=current_user)


@router.get("/", dependencies=[Depends(RateLimiter(times=10, seconds=60))], response_model=List[ContactResponse])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    Отримує список контактів поточного користувача.

    Args:
        skip (int): Кількість контактів, які необхідно пропустити.
        limit (int): Максимальна кількість контактів, які необхідно отримати.
        db (Session): Сеанс бази даних.
        current_user (User): Поточний авторизований користувач.

    Returns:
        List[ContactResponse]: Список контактів.
    """
    contacts = await get_contacts(db, skip=skip, limit=limit, user=current_user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Отримує контакт за ідентифікатором.

    Args:
        contact_id (int): Ідентифікатор контакту.
        db (Session): Сеанс бази даних.
        current_user (User): Поточний авторизований користувач.

    Returns:
        ContactResponse: Контакт або помилка 404, якщо контакт не знайдено.
    """
    db_contact = await get_contact(db, contact_id=contact_id, user=current_user)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Оновлює контакт за ідентифікатором.

    Args:
        contact_id (int): Ідентифікатор контакту.
        contact (ContactUpdate): Нові дані для контакту.
        db (Session): Сеанс бази даних.
        current_user (User): Поточний авторизований користувач.

    Returns:
        ContactResponse: Оновлений контакт або помилка 404, якщо контакт не знайдено.
    """
    db_contact = await repository_contacts.update_contact(db, contact_id=contact_id, contact=contact, user=current_user)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Видаляє контакт за ідентифікатором.

    Args:
        contact_id (int): Ідентифікатор контакту.
        db (Session): Сеанс бази даних.
        current_user (User): Поточний авторизований користувач.

    Returns:
        ContactResponse: Видалений контакт або помилка 404, якщо контакт не знайдено.
    """
    db_contact = await repository_contacts.delete_contact(db, contact_id=contact_id, user=current_user)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.get("/search/", response_model=list[ContactResponse])
async def search_contacts(query: str, db: Session = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)):
    """
    Шукає контакти поточного користувача за запитом.

    Args:
        query (str): Пошуковий запит.
        db (Session): Сеанс бази даних.
        current_user (User): Поточний авторизований користувач.

    Returns:
        list[ContactResponse]: Список знайдених контактів.
    """
    contacts = await repository_contacts.search_contacts(db, query=query, user=current_user)
    return contacts


@router.get("/upcoming-birthdays/", response_model=list[ContactResponse])
async def upcoming_birthdays(db: Session = Depends(get_db),
                             current_user: User = Depends(auth_service.get_current_user)):
    """
    Отримує список контактів з найближчими днями народження.

    Args:
        db (Session): Сеанс бази даних.
        current_user (User): Поточний авторизований користувач.

    Returns:
        list[ContactResponse]: Список контактів з найближчими днями народження.
    """
    contacts = await get_upcoming_birthdays(db, user=current_user)
    return contacts
