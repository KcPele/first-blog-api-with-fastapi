from sqlalchemy.orm import Session
from typing import Union, List
import models
import schemas
from passlib.context import CryptContext



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# users config passward
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)



# handing users
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    # checking first if the user is in the database
    user = get_user_by_username(db=db, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user



def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()



def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    
    db_user = models.User(username=user.username, email=user.email, full_name="", verified=True, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



# //handling post

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()


def create_user_post(*, db: Session, title: str, 
description: Union[str, None] = None, 
image: Union[List, None] = None, created_at: str, user_id: int):
    # this is where your save the image to a bucket and return back the url to use
    # for now it is the image name we are saving
    post_data = schemas.PostCreate(title=title, image=image[0].filename, description=description, created_at=created_at)
    db_post = models.Post(**post_data.dict(), owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


# def crud_delete_single_post(db: Session, post_id: int):
#     stm = models.category.delete().where(models.category.c.id == post_id)
#     print(stm)
#     results = db.execute(stm)
#     db.commit()