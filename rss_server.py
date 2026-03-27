import requests
from bs4 import BeautifulSoup
from flask import Flask, Response

app = Flask(__name__)

rss_data = ""

def rss_uret():
    global rss_data

    try:
        url = "https://eksiseyler.com/"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        }

        r = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(r.text, "html.parser")

        rss_items = ""
        seen = set()
        count = 0

        # 🔥 daha sağlam selector
        for l in soup.select("a[href]"):
            title = l.get_text(strip=True)
            link = l.get("href")

            # relative link fix
            if link and link.startswith("/"):
                link = "https://eksiseyler.com" + link

            if title and link:
                if "eksiseyler.com" in link:
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

        rss_data = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
<title>Ekşi RSS</title>
<link>https://eksiseyler.com</link>
<description>Live RSS Feed</description>
{rss_items}
</channel>
</rss>
"""

        print("RSS güncellendi - item sayısı:", count)

    except Exception as e:
        print("RSS hata:", e)

        rss_data = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
<title>Ekşi RSS</title>
<description>Hata oluştu</description>
</channel>
</rss>"""


@app.route("/")
def home():
    return "RSS server çalışıyor"

@app.route("/rss.xml")
def rss():
    rss_uret()
    return Response(rss_data, mimetype="application/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
