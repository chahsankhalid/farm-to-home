from dotenv import load_dotenv
import os

load_dotenv()

RECHARGE_TOKEN = os.getenv("RECHARGE_API_TOKEN")

SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")

BASE_URL = os.getenv(
    "RECHARGE_BASE_URL",
    "https://api.rechargeapps.com"
)

print("Recharge token loaded:", bool(RECHARGE_TOKEN))

HEADERS = {
    "X-Recharge-Access-Token": RECHARGE_TOKEN,
    "Accept": "application/json",
    "Content-Type": "application/json"
}