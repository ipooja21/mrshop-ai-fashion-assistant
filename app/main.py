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
    allow_origins=["*"],
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
