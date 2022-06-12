#this is a full crud with auth api with a fake db
from fastapi import FastAPI
import users
import posts

app = FastAPI()

app.include_router(users.router)
app.include_router(posts.router)
@app.get("/")
async def index():
    return {"msg":"home page here"}






