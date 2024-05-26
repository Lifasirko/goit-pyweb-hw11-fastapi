from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: Optional[date] = None
    additional_info: Optional[str] = None
    id: Optional[str] = None
    created_at: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class Contact(ContactBase):
    id: int

    class Config:
        from_attributes = True


class ContactResponse(ContactBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: EmailStr
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    password: str
