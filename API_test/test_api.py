import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import io
import os
import zipfile

from db.database import BaseModel, get_db
from main import app

EXPORT_DIR = './output'

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

BaseModel.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def test_db():
    BaseModel.metadata.create_all(bind=engine)
    yield
    BaseModel.metadata.drop_all(bind=engine)

def test_login(test_db):
    response = client.post("/user/login", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(test_db):
    response = client.post("/user/login", data={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 401

def create_test_zip(files):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, content in files.items():
            zip_file.writestr(file_name, content)
    return zip_buffer.getvalue()

def test_upload_file_success(test_db):

    os.makedirs(EXPORT_DIR, exist_ok=True)

    login_response = client.post("/user/login", data={"username": "testuser", "password": "testpassword"})
    access_token = login_response.json()["access_token"]


    valid_files = {
        "A.txt": "Content of A",
        "B.txt": "Content of B",
        "C.txt": "Content of C"
    }
    zip_content = create_test_zip(valid_files)

    response = client.post(
        "/user/upload",
        headers={"Authorization": f"Bearer {access_token}"},
        files={"file": ("test.zip", zip_content, "application/zip")}
    )

    assert response.status_code == 200
    assert "uploaded" in response.json()["message"]
    assert "successfully" in response.json()["message"]

def test_upload_file_missing_required(test_db):
    login_response = client.post("/user/login", data={"username": "testuser", "password": "testpassword"})
    access_token = login_response.json()["access_token"]

    invalid_files = {
        "A.txt": "Content of A",
        "C.txt": "Content of C"
    }
    zip_content = create_test_zip(invalid_files)

    response = client.post(
        "/user/upload",
        headers={"Authorization": f"Bearer {access_token}"},
        files={"file": ("test.zip", zip_content, "application/zip")}
    )

    assert response.status_code == 400
    assert "Missing required file(s)" in response.json()["detail"]

def test_upload_non_zip_file(test_db):
    login_response = client.post("/user/login", data={"username": "testuser", "password": "testpassword"})
    access_token = login_response.json()["access_token"]

    response = client.post(
        "/user/upload",
        headers={"Authorization": f"Bearer {access_token}"},
        files={"file": ("test.txt", b"This is not a ZIP file", "text/plain")}
    )

    assert response.status_code == 400
    assert "Only ZIP files are allowed" in response.json()["detail"]

def test_upload_without_authentication(test_db):
    valid_files = {
        "A.txt": "Content of A",
        "B.txt": "Content of B"
    }
    zip_content = create_test_zip(valid_files)

    response = client.post(
        "/user/upload",
        files={"file": ("test.zip", zip_content, "application/zip")}
    )

    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

