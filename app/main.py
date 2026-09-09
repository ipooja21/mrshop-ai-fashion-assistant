import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.database import init_database

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Mr.Shop AI Fashion Assistant",
    description="Conversational AI fashion assistant API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    # Keep this list explicit.  Browsers do not permit a wildcard origin when
    # credentials are enabled, which made local development needlessly brittle.
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_database()

app.include_router(router)

@app.get("/")
def root():
    return {
        "message": "Welcome to Mr.Shop AI",
        "status": "running",
        "docs": "/docs",
    }
