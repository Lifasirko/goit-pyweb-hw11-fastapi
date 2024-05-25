import redis.asyncio as redis
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from src.config import settings
from src.database.models import User
from src.routes import auth, contacts, users
from src.services.auth import auth_service

load_dotenv()

# Enable CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # додайте інші дозволені джерела
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)


# @app.on_event("shutdown")
# async def shutdown_event():
#     await redis.close()


app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')


@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_root():
    return {"message": "Welcome to the Contact API!!!"}


@app.get("/secret")
async def read_item(current_user: User = Depends(auth_service.get_current_user)):
    return {"message": 'secret router', "owner": current_user.email}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
