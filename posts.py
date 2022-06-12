from fastapi import APIRouter, Query, Path, File, Form,UploadFile, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Union, List
from datetime import datetime, timedelta
from random import randint
import dependencies
import main
# from users import get_current_user
from schemas import User, Post, PostCreate
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
    if post_db.owner.username != owner.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not the owner of these post")
    return post_id

# get all blog post
@router.get("/", response_model=List[Post], status_code=status.HTTP_200_OK)
async def blog_posts(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)):
    return crud.get_posts(db=db, skip=skip, limit=limit)




# post a blog post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Post)
async def blog_post(active_user: User = Depends(users.get_current_user), title: str = Form(...), 
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


# # updata the blog post
# @router.patch("/{post_id}", status_code=status.HTTP_202_ACCEPTED)
# async def blog_post(*, post_id: int = Depends(post_dependency_check), title: Union[str, None] = Form(default=None), 
# description: Union[str, None] = Form(default=None), 
# image: Union[UploadFile, None] = None):
#     stored_post_data = fake_blog_db[post_id]
#     if title is not None:
#         stored_post_data["title"] = title
#     if description is not None:
#         stored_post_data["description"] = description
#     if image is not None:
#         stored_post_data["image"] = [image]
#     return stored_post_data




#delete a blog post
# @router.delete("/{post_id}", status_code=status.HTTP_202_ACCEPTED)
# async def blog_post(post_id: int = Depends(post_dependency_check), db: Session = Depends(dependencies.get_db)):
#     crud.crud_delete_single_post(db, post_id=post_id)
#     return {"msg":"successufully deleted"}



