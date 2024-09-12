import os
import shutil
import uuid
import zipfile
from datetime import datetime, timedelta

import schemas
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# 密碼加密相關
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

# JWT相關設置
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


# 模擬用戶數據庫
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "hashed_password": pwd_context.hash("testpassword"),
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return schemas.UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.User(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

#驗證檔案
def validate_txt_files(temp_dir, file_path, required_files, optional_files):
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()

            unexpected_files = [
                file for file in file_list 
                if not file.endswith('.txt') or file not in required_files + optional_files
            ]
            if unexpected_files:
                raise HTTPException(status_code=400, detail=f"Unexpected or invalid file(s): {', '.join(unexpected_files)}")

            missing_files = [file for file in required_files if file not in file_list]
            if missing_files:
                raise HTTPException(status_code=400, detail=f"Missing required file(s): {', '.join(missing_files)}")

            zip_ref.extractall(temp_dir)
        
        return file_list
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file")



def generate_zip_name():
    return str(uuid.uuid4())[:8] + '.zip'

# 加密
def encrypt_and_zip_files(file_list, temp_dir, export_dir,fernet):
    content_data = {}
    
    for filename in file_list:
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'rb') as file:
            data = file.read()
            if filename.startswith('A'):
                content_data["A"] = data
            elif filename.startswith('B'):
                content_data["B"] = data
            elif filename.startswith('C'):
                content_data["C"] = data
        encrypted_data = fernet.encrypt(data)
        with open(file_path + '.encrypted', 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)
    

    # 壓縮成新的 ZIP 檔案
    zip_filename = generate_zip_name()
    zip_filepath = os.path.join(export_dir, zip_filename)
    print(zip_filepath)
    with zipfile.ZipFile(zip_filepath, 'w') as new_zip:
        for filename in [f"{orifilename}.encrypted" for orifilename in file_list]:
                new_zip.write(os.path.join(temp_dir, filename), arcname=filename)

    return content_data, zip_filepath  

#解密
def decrypt_and_parse_zip(files, zip_file_path, fernet):

    json_data = {}
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            temp_dir = os.path.splitext(zip_file_path)[0] 
            zip_ref.extractall(temp_dir)  
        for filename in files:
            file_path = os.path.join(temp_dir, filename)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as encrypted_file:
                    encrypted_data = encrypted_file.read()
                decrypted_data = fernet.decrypt(encrypted_data)
                print(decrypted_data)
                if filename.startswith('A'):
                    json_data["A"] = decrypted_data
                elif filename.startswith('B'):
                    json_data["B"] = decrypted_data
                elif filename.startswith('C'):
                    json_data["C"] = decrypted_data
        
        return json_data
    finally:
        shutil.rmtree(temp_dir)