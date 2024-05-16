from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from src.database import models
from src.database.db import engine
from src.database.models import User
from src.routes import auth, contacts


# models.Base.metadata.create_all(bind=engine)

app = FastAPI()
# hash_handler = Hash()
# security = HTTPBearer()
app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')


# class UserModel(BaseModel):
#     username: str
#     password: str


@app.get("/")
def read_root():
    return {"message": "Welcome to the Contact API"}


# @app.get("/secret")
# async def read_item(current_user: User = Depends(get_current_user)):
#     return {"message": 'secret router', "owner": current_user.email}
