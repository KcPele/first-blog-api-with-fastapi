from typing import List, Union
from fastapi import UploadFile
from pydantic import BaseModel
from datetime import datetime

class PostBase(BaseModel):
    description: Union[str, None] = None
    image: Union[str, None] = None
    
class PostCreateBase(PostBase):
    title: str
    created_at: datetime
class PostCreate(PostCreateBase):
    pass
class PostUpdate(PostBase):
    title: Union[str, None] = None

class Post(PostCreateBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: Union[str, None] = None
    


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    full_name: Union[str, None] = None
    verified: Union[bool, None] = None
    posts: List[Post] = []

    class Config:
        orm_mode = True