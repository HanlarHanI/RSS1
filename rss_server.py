from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

CACHE = {
    "time": 0,
    "data": ""
}

CACHE_DURATION = 300  # 5 dakika

def rss_uret():
    url = "https://eksiseyler.com/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    links = soup.select("a[href]")

    rss_items = ""
    seen = set()
    count = 0

    for l in links:
        link = l.get("href")

        if not link:
            continue

        if link.startswith("/"):
            link = "https://eksiseyler.com" + link

        if "eksiseyler.com" not in link:
            continue

        title = l.get_text(strip=True)

        # boş title fix
        if not title:
            title = link.split("/")[-1].replace("-", " ")

        if link not in seen:
            seen.add(link)

            rss_items += f"""
<item>
    <title>{title}</title>
    <link>{link}</link>
</item>
"""

            count += 1

        if count >= 20:
            break

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>Ekşi RSS</title>
    <link>https://eksiseyler.com</link>
    <description>Live RSS Feed</description>
    {rss_items}
</channel>
</rss>
"""

    return rss


@app.route("/")
def home():
    return "RSS server çalışıyor"

@app.route("/rss.xml")
def rss():
    global CACHE

    now = time.time()

    # cache kontrol
    if now - CACHE["time"] > CACHE_DURATION:
        try:
            CACHE["data"] = rss_uret()
            CACHE["time"] = now
        except Exception as e:
            return f"Error: {str(e)}"

    return Response(CACHE["data"], mimetype="application/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
