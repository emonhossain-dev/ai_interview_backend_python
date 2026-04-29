from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('postgresql://neondb_owner:npg_KqyMcS5Ck8dG@ep-wild-waterfall-amwyo8bf-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
