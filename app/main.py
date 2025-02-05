from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.utils.middlewares import CreateStateMiddleware
from config import settings
from .models.clean_and_seed_data import drop_database, seed_data
from .routes import codeRouter, authRouter, appRouter, otpRouter
from .models.db import db
from .utils.logger import Logger

ENV = settings.ENV
is_dev = ENV == "dev"

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Logger.warning("You are running in " + ENV + " mode.")
        if is_dev:
            drop_database()

        db.init_db()

        if is_dev:
            seed_data()
    except Exception as e:
        Logger.error(e)
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
    return {}


routes = [codeRouter, otpRouter, authRouter, appRouter]
for route in routes:
    app.include_router(route.router, prefix="/api")