import logging
from datetime import date, timedelta
from typing import List

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate

logger = logging.getLogger(__name__)


async def get_contacts(db: AsyncSession, user: User, skip: int = 0, limit: int = 100) -> List[Contact]:
    result = await db.execute(
        select(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_contact(db: AsyncSession, user: User, contact_id: int):
    result = await db.execute(
        select(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
    )
    return result.scalars().first()


async def cr_contact(db: AsyncSession, user: User, contact: ContactCreate):
    db_contact = Contact(**contact.dict(), user_id=user.id)
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact


async def update_contact(db: AsyncSession, contact_id: int, user: User, contact: ContactUpdate):
    result = await db.execute(
        select(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
    )
    db_contact = result.scalars().first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        await db.commit()
        await db.refresh(db_contact)
    return db_contact


async def delete_contact(db: AsyncSession, contact_id: int, user: User):
    result = await db.execute(
        select(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
    )
    db_contact = result.scalars().first()
    if db_contact:
        await db.delete(db_contact)
        await db.commit()
    return db_contact


async def search_contacts(db: AsyncSession, query: str, user: User):
    result = await db.execute(
        select(Contact).filter(
            and_(
                Contact.user_id == user.id,
                or_(
                    Contact.first_name.ilike(f'%{query}%'),
                    Contact.last_name.ilike(f'%{query}%'),
                    Contact.email.ilike(f'%{query}%')
                )
            )
        )
    )
    return result.scalars().all()


async def get_upcoming_birthdays(db: AsyncSession, user: User):
    today = date.today()
    next_week = today + timedelta(days=7)
    result = await db.execute(
        select(Contact).filter(
            and_(Contact.birthday.between(today, next_week), Contact.user_id == user.id)
        )
    )
    return result.scalars().all()
