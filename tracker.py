import requests
from bs4 import BeautifulSoup
import os

# Load secrets
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TARGET_PRICE = int(os.getenv("TARGET_PRICE"))  # expected lowest price
URL = os.getenv("URL")  # product URL

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def get_price_flipkart(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    price = soup.find("div", {"class": "_30jeq3 _16Jk6d"})
    return int(price.text.replace("₹", "").replace(",", "")) if price else None

def get_price_amazon(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    price = soup.find(id="priceblock_ourprice") or soup.find(id="priceblock_dealprice")
    return int(price.text.replace("₹", "").replace(",", "")) if price else None

if "flipkart.com" in URL:
    price = get_price_flipkart(URL)
else:
    price = get_price_amazon(URL)

if price:
    if price <= TARGET_PRICE:
        send_telegram(f"Price alert! Current price = ₹{price} \n{URL}")
    else:
        print(f"No alert. Current price: ₹{price}")
else:
    print("Could not fetch price")
