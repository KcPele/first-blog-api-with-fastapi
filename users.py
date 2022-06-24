from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks, Path, Security
from pydantic import BaseModel
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jose import JWTError, jwt
from typing import Union, List
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
from dotenv import dotenv_values
# handing database
from sqlalchemy.orm import Session
import crud
import models
import schemas
import dependencies

config = dotenv_values(".env")
# auth conig

ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: List[str] = []

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"me": "Read information about the current user.", "items": "Read post.", "write":"create post", "update":"update only uour item", "delete":"deletes your posts"},
    )

router = APIRouter()


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config["SECRET_KEY"], algorithm=config["ALGORITHM"])
    return encoded_jwt


async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), db: Session = Depends(dependencies.get_db)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, config["SECRET_KEY"], algorithms=config["ALGORITHM"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(current_user: schemas.User = Security(get_current_user, scopes=["me"])):
    if not current_user.verified:
        raise HTTPException(status_code=400, detail="unverified user")
    return current_user





@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# getting a user
@router.get("/users/me/", response_model=schemas.User, description="to check if you have being verified")
async def read_users_me(current_user: schemas.User = Security(get_current_active_user)):
    return current_user

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(dependencies.get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users



# background task
def write_notification(email: str, message=""):
    with open("log.txt", mode="a") as email_file:
        content = f"{email}: {message}"
        email_file.write(content + "\n")
# to be implemented
def verify_user(user):
    user["verified"] = True


@router.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register(*, user: schemas.UserCreate, db: Session = Depends(dependencies.get_db), background_tasks: BackgroundTasks):
    
    db_user_username = crud.get_user_by_username(db=db, username=user.username)
    db_user_email = crud.get_user_by_email(db, email=user.email)
    if db_user_username:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="The username is alredy taken, please try a different one")
    elif db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    background_tasks.add_task(write_notification, user.email, message="please check your email to verify account")
    # background_tasks.add_task(verify_user, fake_users_db[user.username])
    return crud.create_user(db=db, user=user)