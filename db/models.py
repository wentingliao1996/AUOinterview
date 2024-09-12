from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, Text,
                        func)
from sqlalchemy.orm import relationship

from .database import BaseModel, engine


class User(BaseModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    upload_records = relationship("UploadRecord", back_populates="user")


class UploadRecord(BaseModel):
    __tablename__ = "upload_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), ForeignKey("user.username"))
    uuid = Column(String(10), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", back_populates="upload_records")
    record_content = relationship("RecordContent", back_populates="upload_record")


class RecordContent(BaseModel):
    __tablename__ = "record_content"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(String(10), ForeignKey("upload_records.uuid"))
    A = Column(Text, nullable=False)
    B = Column(Text, nullable=False)
    C = Column(Text, nullable=True)


    upload_record = relationship("UploadRecord", back_populates="record_content")

    
BaseModel.metadata.create_all(bind=engine)

                                                                     
    


    