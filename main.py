from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS

from routes.subscription import router as subscription_router
from routes.seeds import router as seeds_router
from routes.webhooks import router as webhook_router

from database import Base, engine
from models.customer import Customer  # noqa: F401
from models.seed_transaction import SeedTransaction  # noqa: F401
from models.reward import Reward  # noqa: F401
from models.redemption import Redemption  # noqa: F401

print("✅ MAIN.PY WITH SEEDS LOADED")

app = FastAPI(
    title="Farm to Home Recharge API",
    version="1.0.0",
)

print("ALLOWED_ORIGINS =", ALLOWED_ORIGINS) 

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Existing Recharge APIs
app.include_router(subscription_router, prefix="/subscription")

# New Seeds APIs
app.include_router(seeds_router)
print(app.routes)

app.include_router(webhook_router)

@app.get("/")
def health():
    return {
        "status": "running",
        "service": "Farm to Home Recharge API",
        "version": "1.0.0"
    }

# Create database tables
Base.metadata.create_all(bind=engine)