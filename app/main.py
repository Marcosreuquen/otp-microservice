from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from contextlib import asynccontextmanager

from config import settings
from .routes import code, mfa, auth
from .models.db import get_session, db


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", status_code=200)
async def root(session: Session = Depends(get_session)):
    print(session)
    return {}

routes = [code, mfa, auth]
for route in routes:
    app.include_router(route.router, prefix="/api")