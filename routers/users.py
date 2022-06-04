from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Union
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
from dotenv import dotenv_values


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "verified": False,
    }
}




config = dotenv_values(".env")
# auth conig

ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
    


class BaseUserModel(BaseModel):
    username: str
    email: Union[str, None] = None

class User(BaseUserModel):
    full_name: Union[str, None] = None
    verified: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str

class RegisterUser(BaseUserModel):
    password: Union[str, int]


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#register a new user
# background email send when a user signs ups
# get all users
# get a users
#change user password


router = APIRouter()

# users config passward
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    # checking first if the user is in the database
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config["SECRET_KEY"], algorithm=config["ALGORITHM"])
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config["SECRET_KEY"], algorithms=config["ALGORITHM"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.verified:
        raise HTTPException(status_code=400, detail="unverified user")
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# getting a user
@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


# //background task
def write_notification(email: str, message=""):
    with open("log.txt", mode="a") as email_file:
        content = f"{email}: {message}"
        email_file.write(content + "\n")

def verify_user(user):
    user["verified"] = True


@router.post("/create/user", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: RegisterUser, background_tasks: BackgroundTasks):
    
    check_user = get_user(fake_users_db, user.username)
    if check_user is not None:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="The username is alredy taken, please try a different one")
    hash_pwd = get_password_hash(user.password)
    db_user_model = UserInDB(username=user.username, email=user.email, full_name="", verified=False, hashed_password=hash_pwd)
    user_model_dict = dict(db_user_model)
    fake_users_db[user.username] = user_model_dict
    background_tasks.add_task(write_notification, user.email, message="please check your email to verify account")
    background_tasks.add_task(verify_user, fake_users_db[user.username])
    return fake_users_db[user.username] 

@router.get("/users")
async def all_users():
    all_users_db = []
    for key in fake_users_db:
        all_users_db.append(fake_users_db[key])
    return all_users_db