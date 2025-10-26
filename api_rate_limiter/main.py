import string
from typing import Union
from logging import getLogger
from fastapi import FastAPI, Depends
from pydantic import BaseModel

from auth import UserLogin, Token, User, get_current_user, login_user

log = getLogger()
app = FastAPI()

class Item(BaseModel):
    id: str
    message: str


items = {}

# Login endpoint
@app.post("/login", response_model=Token)
async def login(user_login: UserLogin):
    return login_user(user_login)

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Protected route example
@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}, this is a protected route!"}

@app.get("/items/{item_id}")
def read_item(item_id: str, q: Union[str, None] = None, current_user: User = Depends(get_current_user)):
    if message := items.get(item_id):
        return message
    return None

@app.post("/items/")
def add_item(item: Item, current_user: User = Depends(get_current_user)):
    items[item.id] = item.message
    log.info(f"{item}")
    return f"item {item} added by {current_user.username}"
    