import os
import shutil
import zipfile
from datetime import datetime, timedelta

import schemas as schemas
import utils as utils
from cryptography.fernet import Fernet
from db.cruds import get_all_record, save_content, save_upload_info_to_db
from db.database import get_db
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

ACCESS_TOKEN_EXPIRE_MINUTES = 30
EXPORT_DIR = './output'

encryption_key = b'_6O_k6GCGprGWMqBq6ap4DScGaqLhVXeIIo0t6HL08Q='
fernet = Fernet(encryption_key)

required_files = ['A.txt', 'B.txt']
optional_files = ['C.txt']

router = APIRouter(tags=["users"], prefix="/user")

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = utils.authenticate_user(utils.fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: schemas.User = Depends(utils.get_current_user),db: Session = Depends(get_db)):

    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are allowed")

    temp_dir = f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    try:
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_list = utils.validate_txt_files(temp_dir, file_path, required_files, optional_files)
        content_data, zip_filepath = utils.encrypt_and_zip_files(file_list, temp_dir, EXPORT_DIR, fernet)
        uuid = os.path.splitext(os.path.basename(zip_filepath))[0]
        
        save_upload_info_to_db(current_user, uuid, db)
        if 'C' not in content_data.keys():
            content_data["C"] = ''
        save_content(uuid, content_data["A"], content_data["B"], content_data["C"], db)

        return {"message": f"{current_user.username} uploaded {uuid} successfully \n content {content_data}"}
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file")

    finally:
        shutil.rmtree(temp_dir)

@router.get("/records")
async def get_records(current_user: schemas.User = Depends(utils.get_current_user),db: Session = Depends(get_db)):

    records_as_dicts = get_all_record(db)

    return records_as_dicts