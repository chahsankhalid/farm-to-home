from dotenv import load_dotenv
import os

load_dotenv()

RECHARGE_TOKEN = os.getenv("RECHARGE_API_TOKEN")
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")

BASE_URL = os.getenv(
    "RECHARGE_BASE_URL",
    "https://api.rechargeapps.com"
)

DATABASE_URL = os.getenv("DATABASE_URL")

SHOPIFY_WEBHOOK_SECRET = os.getenv(
    "SHOPIFY_WEBHOOK_SECRET",
    ""
)

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://farmtohome.pt,"
    "http://localhost:9292,"
    "http://127.0.0.1:9292,"
    "https://extensions.shopifycdn.com"
).split(",")

if not RECHARGE_TOKEN:
    raise RuntimeError("RECHARGE_API_TOKEN is not configured.")

HEADERS = {
    "X-Recharge-Access-Token": RECHARGE_TOKEN,
    "Accept": "application/json",
    "Content-Type": "application/json"
}