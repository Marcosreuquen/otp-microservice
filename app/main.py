from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.utils.middlewares import CreateStateMiddleware
from config import settings
from .models.clean_and_seed_data import drop_database, seed_data
from .routes import codeRouter, authRouter, appRouter, otpRouter
from .routes import healthRouter
from .models.db import db
from .utils.logger import Logger
from app.utils.exceptionHandler import fastapi_exception_handler, ApiException
from app.lib.cache import redis_client, close_redis

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
        # try pinging redis at startup (optional)
        try:
            await redis_client.ping()
            Logger.info("Redis is available")
        except Exception as e:
            Logger.warning(f"Redis not available at startup: {e}")
    except Exception as e:
        Logger.error(e)
    yield
    # Shutdown/cleanup
    try:
        await close_redis()
    except Exception:
        pass

app = FastAPI(lifespan=lifespan)

# Register exception handlers
app.add_exception_handler(Exception, fastapi_exception_handler)
app.add_exception_handler(ApiException, fastapi_exception_handler)

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

# health router (it already defines its own prefix)
app.include_router(healthRouter.router)