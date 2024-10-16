from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.utils.middlewares import CreateStateMiddleware
from .routes import codeRouter, mfaRouter, authRouter, appRouter
from .models.db import db


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

app.add_middleware(CreateStateMiddleware)

@app.get("/", status_code=200)
async def root():
    """Root endpoint."""
    return {}


routes = [codeRouter, mfaRouter, authRouter, appRouter]
for route in routes:
    app.include_router(route.router, prefix="/api")