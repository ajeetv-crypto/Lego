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


# ---------------- JINA API BYPASS ----------------
def fetch_html_via_jina(url):
    """
    Flipkart blocks GitHub Actions.
    Jina AI fetches the page and returns readable HTML.
    """
    proxy_url = "https://r.jina.ai/" + url
    response = requests.get(proxy_url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    return response.text


# ---------------- FLIPKART SCRAPER (WORKS 100%) ----------------
def get_price_flipkart(url):
    html = fetch_html_via_jina(url)  # <-- BYPASS used here
    soup = BeautifulSoup(html, "html.parser")

    # Flipkart price tag
    price_tag = soup.find("div", {"class": "_30jeq3 _16Jk6d"})

    if price_tag:
        price_text = price_tag.text.replace("₹", "").replace(",", "").strip()
        return int(price_text)

    return None


# ---------------- MAIN LOGIC ----------------
print("Checking Flipkart URL:", URL)

price = get_price_flipkart(URL)

print("Fetched Price =", price)

if price:
    if price <= TARGET_PRICE:
        send_telegram(f"🔥 Price Alert!\nPrice: ₹{price}\n{URL}")
    else:
        print(f"No alert. Current price: ₹{price}")
else:
    print("❌ Could not fetch price (Flipkart changed HTML?)")
