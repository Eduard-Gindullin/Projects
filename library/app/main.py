from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from . import models, schemas, auth
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Система управления библиотекой")

# Эндпоинты аутентификации
@app.post("/register/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Эндпоинты для книг
@app.post("/books/", response_model=schemas.Book)
async def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/", response_model=List[schemas.Book])
async def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = db.query(models.Book).offset(skip).limit(limit).all()
    return books

@app.get("/books/{book_id}", response_model=schemas.Book)
async def read_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return book

@app.put("/books/{book_id}", response_model=schemas.Book)
async def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    for key, value in book.dict().items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete("/books/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    db.delete(db_book)
    db.commit()
    return {"message": "Книга успешно удалена"}

# Эндпоинты для читателей
@app.post("/readers/", response_model=schemas.Reader)
async def create_reader(reader: schemas.ReaderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_reader = models.Reader(**reader.dict())
    db.add(db_reader)
    db.commit()
    db.refresh(db_reader)
    return db_reader

@app.get("/readers/", response_model=List[schemas.Reader])
async def read_readers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    readers = db.query(models.Reader).offset(skip).limit(limit).all()
    return readers

@app.get("/readers/{reader_id}", response_model=schemas.Reader)
async def read_reader(reader_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    reader = db.query(models.Reader).filter(models.Reader.id == reader_id).first()
    if reader is None:
        raise HTTPException(status_code=404, detail="Читатель не найден")
    return reader

# Эндпоинты для выдачи книг
@app.post("/borrow/", response_model=schemas.BorrowedBook)
async def borrow_book(borrow: schemas.BorrowedBookCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Проверка существования книги и наличия доступных экземпляров
    book = db.query(models.Book).filter(models.Book.id == borrow.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    if book.copies_available <= 0:
        raise HTTPException(status_code=400, detail="Нет доступных экземпляров")

    # Проверка существования читателя и количества взятых книг
    reader = db.query(models.Reader).filter(models.Reader.id == borrow.reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Читатель не найден")
    
    active_borrows = db.query(models.BorrowedBook).filter(
        models.BorrowedBook.reader_id == reader.id,
        models.BorrowedBook.return_date == None
    ).count()
    
    if active_borrows >= 3:
        raise HTTPException(status_code=400, detail="Читатель уже взял максимальное количество книг")

    # Создание записи о выдаче и обновление количества книг
    db_borrow = models.BorrowedBook(**borrow.dict())
    book.copies_available -= 1
    
    db.add(db_borrow)
    db.commit()
    db.refresh(db_borrow)
    return db_borrow

@app.post("/return/{borrow_id}")
async def return_book(borrow_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    borrow = db.query(models.BorrowedBook).filter(models.BorrowedBook.id == borrow_id).first()
    if not borrow:
        raise HTTPException(status_code=404, detail="Запись о выдаче не найдена")
    if borrow.return_date:
        raise HTTPException(status_code=400, detail="Книга уже возвращена")

    book = db.query(models.Book).filter(models.Book.id == borrow.book_id).first()
    book.copies_available += 1
    borrow.return_date = datetime.utcnow()
    
    db.commit()
    return {"message": "Книга успешно возвращена"}

@app.get("/readers/{reader_id}/borrowed", response_model=List[schemas.BorrowedBook])
async def get_reader_borrowed_books(reader_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    borrowed_books = db.query(models.BorrowedBook).filter(
        models.BorrowedBook.reader_id == reader_id,
        models.BorrowedBook.return_date == None
    ).all()
    return borrowed_books 