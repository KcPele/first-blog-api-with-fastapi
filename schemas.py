from typing import List, Union
from fastapi import UploadFile
from pydantic import BaseModel
from datetime import datetime

class PostBase(BaseModel):
    title: str
    description: Union[str, None] = None
    image: Union[str, None] = None
    created_at: datetime

class PostCreate(PostBase):
    pass


class Post(PostBase):
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