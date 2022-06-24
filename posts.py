from fastapi import APIRouter, Query, Path, File, Form,UploadFile, HTTPException, status, Depends, Security, BackgroundTasks
from pydantic import BaseModel
from typing import Union, List
from datetime import datetime, timedelta
from random import randint
import dependencies
import main
# from users import get_current_user
from schemas import User, Post, PostCreate, PostUpdate
import users
from sqlalchemy.orm import Session
import crud
import models
import dependencies
router = APIRouter(
    prefix="/posts",
)



async def post_dependency_check(post_id: int = Path(default=None), owner: User = Depends(users.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    post_db = crud.get_post(db, post_id=post_id)
    if not post_db:
        raise HTTPException(detail="the data with these id does not exist", status_code=status.HTTP_404_NOT_FOUND)
    if post_db.owner.id != owner.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not the owner of these post")
    return post_db

# get all blog post
@router.get("/", response_model=List[Post], status_code=status.HTTP_200_OK)
async def blog_posts(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)):
    return crud.get_posts(db=db, skip=skip, limit=limit)




# post a blog post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Post)
async def blog_post(current_user: User = Security(users.get_current_user, scopes=["write"]), title: str = Form(...), 
description: Union[str, None] = Form(default=None), 
image: Union[List[UploadFile], None] = File(default=None),
db: Session = Depends(dependencies.get_db)):
    created_at = datetime.now()
    # post_data = PostCreate(title=title, image=image, description=description, created_at=created_at)
    return crud.create_user_post(db=db, title=title, image=image, description=description, created_at=created_at, user_id=active_user.id)
    # return crud.create_user_post(db, post=post_data, user_id=active_user.id)

# get a blog post
@router.get("/{post_id}", response_model=Post)
async def blog_post(post_id: int = Path(default=None), db: Session = Depends(dependencies.get_db)):
    post_data = crud.get_post(db, post_id=post_id)
    if not post_data:
        raise HTTPException(detail="the data with these id was not found", status_code=status.HTTP_404_NOT_FOUND)
    return post_data


@router.patch("/{post_id}", response_model=Post)
# this will change becase of the image. it will be form type not json
# it will be similar to blog_post route
def update_post_for_user(*, post_data: Post = Security(post_dependency_check, scopes=["update"]), post: PostUpdate, db: Session = Depends(dependencies.get_db), current_user: User = Security(users.get_current_user, scopes=["update"])):
    return crud.update_user_post(db=db, payload=post, post_data=post_data)


@router.delete("/{post_id}")
def delete_posts(post_data: Post = Security(post_dependency_check, scopes=["delete"]), db: Session = Depends(dependencies.get_db)):
    crud.delete_post(db, post_data=post_data)
    return 'successfully deleted'

