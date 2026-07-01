from dotenv import load_dotenv
import os

load_dotenv()

RECHARGE_TOKEN = os.getenv("RECHARGE_API_TOKEN")
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
API_KEY = os.getenv("API_KEY")

BASE_URL = os.getenv(
    "RECHARGE_BASE_URL",
    "https://api.rechargeapps.com"
)

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://farmtohome.pt,http://localhost:9292,http://127.0.0.1:9292"
).split(",")

print("Recharge token loaded:", bool(RECHARGE_TOKEN))

HEADERS = {
    "X-Recharge-Access-Token": RECHARGE_TOKEN,
    "Accept": "application/json",
    "Content-Type": "application/json"
}