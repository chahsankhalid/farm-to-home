from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.subscription import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://farmtohome.pt",
        "http://localhost:9292",
        "http://127.0.0.1:9292"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/subscription")