import requests
import os
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TARGET_PRICE = int(os.getenv("TARGET_PRICE"))
URL = os.getenv("URL")

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(api_url, data=payload)

def extract_pid(url):
    # Extract the "itmb0b862b085ec2" part
    m = re.search(r'/p/([^/?]+)', url)
    if m:
        return m.group(1)

    # Fallback: pid=XXXX
    m = re.search(r'pid=([A-Z0-9]+)', url, re.I)
    if m:
        return m.group(1)

    return None

def get_price_flipkart(url):
    pid = extract_pid(url)
    if not pid:
        print("❌ Could not extract PID")
        return None

    api_url = f"https://www.flipkart.com/api/3/product-summary/sku/{pid}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Origin": "https://www.flipkart.com",
        "Referer": url
    }

    resp = requests.get(api_url, headers=headers, timeout=15)

    if resp.status_code != 200:
        print("❌ API failed:", resp.status_code)
        return None

    data = resp.json()
    try:
        price = (
            data["RESPONSE"]["kartData"]["primaryProduct"]["value"]
                ["price"]["finalPrice"]["value"]
        )
        return int(price)
    except Exception as e:
        print("❌ JSON parse error:", e)
        return None

print("Checking URL:", URL)
price = get_price_flipkart(URL)
print("Fetched Price =", price)

if price is not None:
    if price <= TARGET_PRICE:
        send_telegram(f"🔥 Price alert!\nCurrent price = ₹{price}\n{URL}")
    else:
        print("No alert. Current price:", price)
else:
    print("❌ Could not fetch price.")
