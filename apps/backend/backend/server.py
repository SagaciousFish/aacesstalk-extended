from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from py_database.database import create_db_and_tables
from backend.database import engine
from backend.routers import dyad


@asynccontextmanager
async def server_lifespan(app: FastAPI):
    print("Server launched.")
    await create_db_and_tables(engine)

    yield

    # Cleanup logic will come below.

app = FastAPI(lifespan=server_lifespan)

# Setup routers
app.include_router(
    dyad.router,
    prefix="/api/v1/dyad"
)



# Setup middlewares
origins = [
    "http://localhost:3000",
    "localhost:3000",
    "http://localhost:8000",
    "localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-processing-time", "X-request-id", "X-context-id"]
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = perf_counter()
    response = await call_next(request)
    end = perf_counter()
    response.headers["X-processing-time"] = str(end - start)
    return response


@app.middleware("http")
async def pass_request_ids_header(request: Request, call_next):
    response = await call_next(request)

    if "X-request-id" in request.headers:
        response.headers["X-request-id"] = request.headers["x-request-id"]

    if "X-context-id" in request.headers:
        response.headers["X-context-id"] = request.headers["x-context-id"]

    return response
