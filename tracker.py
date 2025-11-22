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

def extract_product_id(url):
    # 1. Try pid=XXXX
    m = re.search(r"pid=([A-Z0-9]+)", url)
    if m:
        return m.group(1)
    # 2. Try /p/<product-id>
    m = re.search(r"/p/([A-Za-z0-9\-]+)", url)
    if m:
        return m.group(1)
    # fallback: load page HTML and search for productId
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        html = resp.text
        m2 = re.search(r'"productId":"([A-Z0-9]+)"', html)
        if m2:
            return m2.group(1)
    except Exception as e:
        print("Error extracting PID from HTML:", e)
    return None

def get_price_flipkart_api(url):
    pid = extract_product_id(url)
    if not pid:
        print("❌ Could not extract PID from URL")
        return None

    api_url = f"https://www.flipkart.com/api/3/page/dynamic/product?pid={pid}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(api_url, headers=headers)
    if resp.status_code != 200:
        print("❌ API failed, status:", resp.status_code)
        return None

    data = resp.json()
    try:
        price = data["RESPONSE"]["productInfo"]["value"]["pricing"]["finalPrice"]["value"]
        return int(price)
    except Exception as e:
        print("❌ Error parsing API JSON:", e)
        return None

print("Checking URL:", URL)
price = get_price_flipkart_api(URL)
print("Fetched Price =", price)

if price is not None:
    if price <= TARGET_PRICE:
        send_telegram(f"🔥 Price alert!\nCurrent price = ₹{price}\n{URL}")
    else:
        print(f"No alert. Current price: ₹{price}")
else:
    print("❌ Could not fetch price.")
