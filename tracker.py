import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TARGET_PRICE = int(os.getenv("TARGET_PRICE"))
URL = os.getenv("URL")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

# ----------- JINA BYPASS REQUEST -----------
def bypass_get(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    # Jina proxy bypasses Flipkart/Amazon block
    proxy_url = f"https://r.jina.ai/{url}"
    return requests.get(proxy_url, headers=headers, timeout=20)

# ----------- Flipkart scraper -----------
def get_price_flipkart(url):
    page = bypass_get(url)  # <-- Use bypass instead of direct request
    soup = BeautifulSoup(page.text, "html.parser")

    price_tag = soup.find("div", {"class": "_30jeq3 _16Jk6d"})
    if price_tag:
        return int(price_tag.text.replace("₹", "").replace(",", "").strip())
    return None

# ---------- MAIN ----------
print("Checking URL:", URL)

price = get_price_flipkart(URL)
print("Fetched Price =", price)

if price:
    if price <= TARGET_PRICE:
        send_telegram(f"🔥 Price alert!\nCurrent price = ₹{price}\n{URL}")
    else:
        print(f"No alert. Current price: ₹{price}")
else:
    print("❌ Could not fetch price via Jina bypass.")
