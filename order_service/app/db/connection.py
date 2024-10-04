from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'sqlite:///.sql.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
)

# # SQL Server connection string using pyodbc
# SQLALCHEMY_DATABASE_URL = "mssql+pyodbc://py:22p=VBL@py@10.20.20.107/fastapi?driver=ODBC+Driver+17+for+SQL+Server"
# # Create the SQLAlchemy engine
# engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
