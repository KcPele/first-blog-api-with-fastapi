from fastapi import HTTPException, Path, status, Depends
# import routers.posts as posts
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



