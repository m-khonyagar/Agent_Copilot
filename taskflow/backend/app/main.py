import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("./workspace")
FRONTEND_BUILD = Path("./frontend/build")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from app.models.database import init_db

    await init_db()
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    logger.info("Database initialised and workspace directory ready.")
    yield
    # Shutdown (nothing special needed)


app = FastAPI(title="TaskFlow AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from app.api.artifacts import router as artifacts_router
from app.api.tasks import router as tasks_router

app.include_router(tasks_router)
app.include_router(artifacts_router)


# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "service": "TaskFlow AI"}


# Serve frontend static files if the build directory exists
if FRONTEND_BUILD.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_BUILD), html=True), name="static")
