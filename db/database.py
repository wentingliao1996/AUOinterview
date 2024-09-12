import pymysql
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

pymysql.install_as_MySQLdb()


DATABASE_URL = 'mysql+pymysql://user:userpassword@mysql:3306/testdb'

def init_database(database_url):
    engine = create_engine(database_url, connect_args={"charset": "utf8"})
    sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, sessionlocal

engine, sessionlocal = init_database(DATABASE_URL)
BaseModel = declarative_base()


def get_db():
    db: Session = sessionlocal()
    try:
        yield db
    finally:
        db.close()


