from dotenv import load_dotenv
import os

load_dotenv()

RECHARGE_TOKEN = os.getenv("RECHARGE_API_TOKEN")

SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")

BASE_URL = "https://api.rechargeapps.com"

print("Recharge Token Loaded:", RECHARGE_TOKEN[:15] + "..." if RECHARGE_TOKEN else "None")

HEADERS = {
    "X-Recharge-Access-Token": RECHARGE_TOKEN,
    "Accept": "application/json",
    "Content-Type": "application/json"
}