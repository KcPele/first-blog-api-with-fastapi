from fastapi import APIRouter, Query, Path, File, Form,UploadFile, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Union, List
from datetime import datetime, timedelta
from random import randint
import dependencies
import main
from .users import  get_current_user, get_current_active_user, User
router = APIRouter(
    prefix="/posts",
)

fake_blog_db = {
    1: {
        "id": 1,
        "owner": "kcpele",
        "title": "first post",
        "image": [],
        "description": "graet",
        "created_at": "2022-06-04T13:46:15.705364"
    }
    
}


class Post(BaseModel):
    id: int
    owner: str 
    title: str
    image: Union[List[UploadFile], None]
    # image: Optional[str] = None
    description: Union[str, None]
    created_at: datetime


# get all blog post
@router.get("/", status_code=status.HTTP_200_OK)
async def blog_post():
    all_post = []
    for key in fake_blog_db:
        all_post.append(fake_blog_db[key])
    return all_post




# post a blog post
@router.post("/", status_code=status.HTTP_201_CREATED)
async def blog_post(owner: User = Depends(get_current_user), title: str = Form(...), 
description: Union[str, None] = Form(default=None), 
image: Union[List[UploadFile], None] = File(default=None)):
    id = randint(3, 100)
    created_at = datetime.now()
    post_data = Post(id=id, owner=owner.username, title=title, image=image, description=description, created_at=created_at)
    post_dict = dict(post_data)

    fake_blog_db[id] = post_dict
    print(fake_blog_db)
    return {"msg": "uploaded successfully"}
# get a blog post
@router.get("/{post_id}")
async def blog_post(post_id: int = Path(default=None)):
    if post_id not in fake_blog_db:
        raise HTTPException(detail="the data with these id does not exist", status_code=status.HTTP_404_NOT_FOUND)
    data = fake_blog_db[post_id]
    return data


# updata the blog post
@router.patch("/{post_id}", status_code=status.HTTP_202_ACCEPTED)
async def blog_post(*, post_id: int = Depends(dependencies.post_dependency_check), title: Union[str, None] = Form(default=None), 
description: Union[str, None] = Form(default=None), 
image: Union[UploadFile, None] = None):
    stored_post_data = fake_blog_db[post_id]
    if title is not None:
        stored_post_data["title"] = title
    if description is not None:
        stored_post_data["description"] = description
    if image is not None:
        stored_post_data["image"] = [image]
    return stored_post_data




#delete a blog post
@router.delete("/{post_id}", status_code=status.HTTP_202_ACCEPTED)
async def blog_post(post_id: int = Depends(dependencies.post_dependency_check)):
    del fake_blog_db[post_id]
    return {"msg":"successufully deleted"}



