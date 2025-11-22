import requests
import os
import json
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TARGET_PRICE = int(os.getenv("TARGET_PRICE"))
URL = os.getenv("URL")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def extract_product_id(url):
    """Extract product ID from Flipkart URL (works for any format)."""
    match = re.search(r"pid=([A-Z0-9]+)", url)
    if match:
        return match.group(1)
    return None

def get_price_flipkart_api(url):
    pid = extract_product_id(url)
    if not pid:
        print("❌ Could not extract PID from URL")
        return None

    api_url = f"https://www.flipkart.com/api/3/page/dynamic/product?pid={pid}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(api_url, headers=headers)
    if r.status_code != 200:
        print("❌ API call failed")
        return None

    data = r.json()

    try:
        price = (
            data["RESPONSE"]["productInfo"]["value"]["pricing"]["finalPrice"]["value"]
        )
        return int(price)
    except:
        return None

print("Checking URL:", URL)

price = get_price_flipkart_api(URL)

print("Fetched Price =", price)

if price:
    if price <= TARGET_PRICE:
        send_telegram(f"🔥 Price alert!\nCurrent price = ₹{price}\n{URL}")
    else:
        print(f"No alert. Current price: ₹{price}")
else:
    print("❌ Could not fetch price")
