"""Main FastAPI application for PlayRef."""

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import api_router
from backend.app.config import settings
from backend.app.db.session import get_engine
from backend.app.ingestion.indexer import get_qdrant_client, init_collection
from backend.app.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure database and Qdrant collection
    logger.info("Starting up PlayRef API server...")
    await get_engine()
    q_client = get_qdrant_client()
    init_collection(q_client, collection_name=settings.qdrant_collection, recreate=False)
    yield
    logger.info("Shutting down PlayRef API server...")


app = FastAPI(
    title="PlayRef API",
    description="Grounded football Laws of the Game conversational assistant",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS middleware for Next.js frontend (Phase 3+)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id_and_timing(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    request.state.request_id = request_id

    response = await call_next(request)

    process_time = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = str(process_time)
    return response


app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
