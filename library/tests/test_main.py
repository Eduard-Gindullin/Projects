import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
import os
from dotenv import load_dotenv

load_dotenv()

# Использование SQLite в памяти для тестирования
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

def test_create_user(client):
    response = client.post(
        "/register/",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

def test_login(client):
    # Сначала создаем пользователя
    client.post(
        "/register/",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    
    # Затем пробуем войти
    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_create_book_without_token(client):
    response = client.post(
        "/books/",
        json={
            "title": "Test Book",
            "author": "Test Author",
            "publication_year": 2024,
            "isbn": "1234567890",
            "copies_available": 1
        }
    )
    assert response.status_code == 401

def test_create_and_borrow_book(client):
    # Создаем пользователя и получаем токен
    client.post(
        "/register/",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    login_response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создаем книгу
    book_response = client.post(
        "/books/",
        headers=headers,
        json={
            "title": "Test Book",
            "author": "Test Author",
            "publication_year": 2024,
            "isbn": "1234567890",
            "copies_available": 1
        }
    )
    assert book_response.status_code == 200
    book_id = book_response.json()["id"]

    # Создаем читателя
    reader_response = client.post(
        "/readers/",
        headers=headers,
        json={
            "name": "Test Reader",
            "email": "reader@example.com"
        }
    )
    assert reader_response.status_code == 200
    reader_id = reader_response.json()["id"]

    # Берем книгу
    borrow_response = client.post(
        "/borrow/",
        headers=headers,
        json={
            "book_id": book_id,
            "reader_id": reader_id
        }
    )
    assert borrow_response.status_code == 200

    # Пробуем взять ту же книгу снова (должно завершиться ошибкой, так как нет доступных экземпляров)
    borrow_response = client.post(
        "/borrow/",
        headers=headers,
        json={
            "book_id": book_id,
            "reader_id": reader_id
        }
    )
    assert borrow_response.status_code == 400

def test_reader_borrow_limit(client):
    # Создаем пользователя и получаем токен
    client.post(
        "/register/",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    login_response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создаем читателя
    reader_response = client.post(
        "/readers/",
        headers=headers,
        json={
            "name": "Test Reader",
            "email": "reader@example.com"
        }
    )
    reader_id = reader_response.json()["id"]

    # Создаем 4 книги
    book_ids = []
    for i in range(4):
        book_response = client.post(
            "/books/",
            headers=headers,
            json={
                "title": f"Test Book {i}",
                "author": "Test Author",
                "publication_year": 2024,
                "isbn": f"123456789{i}",
                "copies_available": 1
            }
        )
        book_ids.append(book_response.json()["id"])

    # Берем 3 книги (должно пройти успешно)
    for i in range(3):
        response = client.post(
            "/borrow/",
            headers=headers,
            json={
                "book_id": book_ids[i],
                "reader_id": reader_id
            }
        )
        assert response.status_code == 200

    # Пробуем взять 4-ю книгу (должно завершиться ошибкой)
    response = client.post(
        "/borrow/",
        headers=headers,
        json={
            "book_id": book_ids[3],
            "reader_id": reader_id
        }
    )
    assert response.status_code == 400 