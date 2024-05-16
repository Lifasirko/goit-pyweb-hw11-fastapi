from datetime import date, timedelta
from typing import List

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from src.database import models
from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate


async def get_contacts(db: Session, user: User, skip: int = 0, limit: int = 100) -> List[Contact]:
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(db: Session, user: User, contact_id: int):
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(db: Session, user: User, contact: ContactCreate):
    db_contact = Contact(**contact.dict(), user=user)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def update_contact(db: Session, contact_id: int, user: User, contact: ContactUpdate):
    db_contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


async def delete_contact(db: Session, contact_id: int, user: User):
    db_contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact


async def search_contacts(db: Session, query: str, user: User):
    return db.query(Contact).filter(
        and_(
            Contact.user_id == user.id,
            or_(
                Contact.first_name.ilike(f'%{query}%'),
                Contact.last_name.ilike(f'%{query}%'),
                Contact.email.ilike(f'%{query}%')
            )
        )
    ).all()


async def get_upcoming_birthdays(db: Session, user: User):
    today = date.today()
    next_week = today + timedelta(days=7)
    return db.query(models.Contact).filter(
        and_(models.Contact.birthday.between(today, next_week), Contact.user_id == user.id)
    ).all()
