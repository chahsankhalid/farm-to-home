from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS
from routes.subscription import router

app = FastAPI(
    title="Farm to Home Recharge API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/subscription")


@app.get("/")
def health():
    return {
        "status": "running",
        "service": "Farm to Home Recharge API",
        "version": "1.0.0"
    }