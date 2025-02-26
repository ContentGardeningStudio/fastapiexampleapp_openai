from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi.security import OAuth2PasswordBearer
from fastapi_limiter import FastAPILimiter

from app.core.database import SessionLocal

from fastapi import FastAPI


# db connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# rate limiter
@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_connection = redis.from_url("redis://localhost:6379", encoding="utf8")
    await FastAPILimiter.init(redis_connection)
    yield
    await FastAPILimiter.close()
