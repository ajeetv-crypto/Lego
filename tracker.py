import requests
from bs4 import BeautifulSoup
import os

# Load secrets
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TARGET_PRICE = int(os.getenv("TARGET_PRICE"))
URL = os.getenv("URL")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

# ---------------- AMAZON SCRAPER ----------------
def get_price_amazon(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")

    # Amazon updated selector
    price_tag = soup.select_one("#corePrice_feature_div .a-price-whole")

    if price_tag:
        price_text = price_tag.text.replace(",", "").replace("₹", "").strip()
        return int(price_text)
    return None

# ---------------- FLIPKART SCRAPER ----------------
def get_price_flipkart(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")

    price_tag = soup.find("div", {"class": "_30jeq3 _16Jk6d"})

    if price_tag:
        price_text = price_tag.text.replace(",", "").replace("₹", "").strip()
        return int(price_text)
    return None

# --------------------------------------------------

print("Checking URL:", URL)

if "flipkart.com" in URL:
    price = get_price_flipkart(URL)
else:
    price = get_price_amazon(URL)

print("Fetched Price =", price)

if price:
    if price <= TARGET_PRICE:
        send_telegram(f"🔥 Price alert!\nCurrent price = ₹{price}\n{URL}")
    else:
        print(f"No alert. Current price: ₹{price}")
else:
    print("❌ Could not fetch price. HTML structure changed.")
