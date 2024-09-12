
from db.models import RecordContent, UploadRecord
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session, selectinload


def save_upload_info_to_db(current_user, uuid, db: Session):
    upload_record = UploadRecord(
            username=current_user.username,  
            uuid=uuid
        )
    db.add(upload_record)
    db.commit()
    db.refresh(upload_record)

def save_content(uuid, A, B, C, db: Session):
    record_content = RecordContent(
            uuid=uuid,
            A=A, 
            B=B, 
            C=C
        )
    db.add(record_content)
    db.commit()
    db.refresh(record_content)

def get_all_record(db: Session):

    query = select(UploadRecord).order_by(desc(UploadRecord.created_at))
    query = query.options(
        selectinload(UploadRecord.record_content)
    )
    result = db.execute(query)
    upload_records = result.scalars().all()
    return upload_records

