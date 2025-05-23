from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Схемы пользователей
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

# Схемы книг
class BookBase(BaseModel):
    title: str
    author: str
    publication_year: Optional[int] = None
    isbn: Optional[str] = None
    copies_available: int = 1
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int

    class Config:
        orm_mode = True

# Схемы читателей
class ReaderBase(BaseModel):
    name: str
    email: EmailStr

class ReaderCreate(ReaderBase):
    pass

class Reader(ReaderBase):
    id: int

    class Config:
        orm_mode = True

# Схемы выданных книг
class BorrowedBookBase(BaseModel):
    book_id: int
    reader_id: int

class BorrowedBookCreate(BorrowedBookBase):
    pass

class BorrowedBook(BorrowedBookBase):
    id: int
    borrow_date: datetime
    return_date: Optional[datetime] = None

    class Config:
        orm_mode = True

# Схемы токенов
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 