import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, Response

app = Flask(__name__)

rss_data = ""

def rss_uret():
    global rss_data

    url = "https://eksiseyler.com/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    links = soup.find_all("a")

    rss_items = ""
    seen = set()
    count = 0

    for l in links:
        title = l.get_text(strip=True)
        link = l.get("href")

        if link and not link.startswith("http"):
            link = "https://eksiseyler.com" + link

        if (
            title
            and link
            and "eksiseyler.com" in link
            and len(title) > 10
        ):
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

    print("RSS güncellendi")


def background_loop():
    while True:
        rss_uret()
        time.sleep(600)


@app.route("/rss.xml")
def rss():
    return Response(rss_data, mimetype="application/xml")


if __name__ == "__main__":
    import threading

    t = threading.Thread(target=background_loop)
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port=8000)