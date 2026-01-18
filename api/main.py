from fastapi import FastAPI
from .database import engine
from . import schemas

app = FastAPI(title="Telegram Corpus API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Telegram Corpus API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
