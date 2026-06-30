from fastapi import FastAPI
from routes.subscription import router as subscription_router

app = FastAPI(
    title="Farm to Home Subscription API",
    version="1.0.0"
)

app.include_router(subscription_router)


@app.get("/")
def root():
    return {
        "status": "running"
    }