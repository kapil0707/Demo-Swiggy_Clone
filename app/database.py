# This file handles database session management and connection
from sqlalchemy import create_engine 
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker


from .config import settings

# This URL should be fetched from environment variables
# Database URL syntax:
# dialect+driver://user:password@host:port/database_name
# - dialect: The type of database (e.g., postgresql, mysql, sqlite)
# - driver: Optional, the DBAPI driver (e.g., psycopg2 for postgresql, defaults if omitted)
# - user: Database username
# - password: Database password
# - host: Database server hostname or IP address
# - port: Database server port number
# - database_name: The name of the database to connect to

#SQLALCHEMY_DATABASE_URL = "postgresql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"

SQLALCHEMY_DATABASE_URL = (
    "postgresql://{settings.database_user}:{settings.database_password}"
    "@{settings.database_host}:{settings.database_port}/"
    "{settings.database_name}"
    )


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()