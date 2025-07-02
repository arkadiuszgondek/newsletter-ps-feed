import feedparser
import json
from datetime import datetime, timedelta, timezone
import re
import requests
from feedgen.feed import FeedGenerator
import hashlib
import os
from html import unescape
from bs4 import BeautifulSoup

FEED_URLS = [
    "https://przegladsportowy.onet.pl/.feed",
    "https://przegladsportowy.onet.pl/pilka-nozna.feed",
    "https://przegladsportowy.onet.pl/tenis.feed",
    "https://przegladsportowy.onet.pl/siatkowka.feed",
    "https://przegladsportowy.onet.pl/koszykowka.feed",
    "https://przegladsportowy.onet.pl/zuzel.feed",
    "https://przegladsportowy.onet.pl/alpinizm.feed",
    "https://przegladsportowy.onet.pl/ofsajd.feed",
    "https://przegladsportowy.onet.pl/czas-na-bieganie.feed",
    "https://przegladsportowy.onet.pl/esportmania.feed",
    "https://przegladsportowy.onet.pl/futbol-amerykanski.feed",
    "https://przegladsportowy.onet.pl/hokej-na-lodzie.feed",
    "https://przegladsportowy.onet.pl/jezdziectwo.feed",
    "https://przegladsportowy.onet.pl/kolarstwo.feed",
    "https://przegladsportowy.onet.pl/paraolimpiada.feed",
    "https://przegladsportowy.onet.pl/snooker.feed",
    "https://przegladsportowy.onet.pl/badminton.feed",
    "https://przegladsportowy.onet.pl/sporty-zimowe/biegi-narciarskie.feed",
    "https://przegladsportowy.onet.pl/felietony.feed",
    "https://przegladsportowy.onet.pl/pilka-nozna/futsal.feed",
    "https://przegladsportowy.onet.pl/hokej-na-trawie.feed",
    "https://przegladsportowy.onet.pl/judo.feed",
    "https://przegladsportowy.onet.pl/lekkoatletyka.feed",
    "https://przegladsportowy.onet.pl/plywanie.feed",
    "https://przegladsportowy.onet.pl/rugby.feed",
    "https://przegladsportowy.onet.pl/sport-akademicki.feed",
    "https://przegladsportowy.onet.pl/baseball.feed",
    "https://przegladsportowy.onet.pl/boks.feed",
    "https://przegladsportowy.onet.pl/fitness-i-porady.feed",
    "https://przegladsportowy.onet.pl/gimnastyka.feed",
    "https://przegladsportowy.onet.pl/lucznictwo.feed",
    "https://przegladsportowy.onet.pl/igrzyska-olimpijskie.feed",
    "https://przegladsportowy.onet.pl/mma.feed",
    "https://przegladsportowy.onet.pl/piecioboj-nowoczesny.feed",
    "https://przegladsportowy.onet.pl/sporty-zimowe/biathlon.feed",
    "https://przegladsportowy.onet.pl/drift-masters.feed",
    "https://przegladsportowy.onet.pl/formula-1.feed",
    "https://przegladsportowy.onet.pl/golf.feed",
    "https://przegladsportowy.onet.pl/inne-sporty.feed",
    "https://przegladsportowy.onet.pl/sporty-zimowe/lyzwiarstwo.feed",
    "https://przegladsportowy.onet.pl/motorowe.feed",
    "https://przegladsportowy.onet.pl/pilka-reczna.feed",
    "https://przegladsportowy.onet.pl/podnoszenie-ciezarow.feed",
    "https://przegladsportowy.onet.pl/sporty-zimowe/skoki-narciarskie.feed",
    "https://przegladsportowy.onet.pl/sporty-lotnicze.feed"
]
CACHE_FILE = 'cache.json'
OUTPUT_FILE = 'docs/rss.xml'
RETENTION_DAYS = 7

def extract_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for img in soup.find_all('img'):
        img.decompose()
    return unescape(soup.get_text(strip=True))

def get_category_from_url(url):
    match = re.search(r"onet\.pl/(.*?).feed", url)
    return match.group(1) if match else "inne"

def generate_entry_id(link):
    return hashlib.md5(link.encode('utf-8')).hexdigest()

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def update_cache():
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=RETENTION_DAYS)
    cache = load_cache()

    for url in FEED_URLS:
        feed = feedparser.parse(url)
        category = get_category_from_url(url)
        for entry in feed.entries:
            entry_id = generate_entry_id(entry.link)
            published = datetime(*entry.published_parsed[:6])
            if entry_id not in cache or published > datetime.fromisoformat(cache[entry_id]["published"]):

                # pobierz cały XML ręcznie i szukaj <summary> po linku
                entry_url = entry.link
                response = requests.get(url)
                raw_xml = response.text

                pattern = rf"<entry>.*?<link[^>]*?href=['\"]{re.escape(entry_url)}['\"].*?</link>.*?<summary[^>]*><!\[CDATA\[(.*?)\]\]></summary>.*?</entry>"
                match = re.search(pattern, raw_xml, re.DOTALL)

                summary_raw = ""
                if match:
                    summary_raw = match.group(1)


                cleaned = ""
                if summary_raw:
                    cleaned = re.sub(r'<img[^>]*>', '', summary_raw, flags=re.IGNORECASE).strip()
                    cleaned = re.sub(r'<[^>]+>', '', cleaned).strip()

                
                cache[entry_id] = {
                    "title": entry.title,
                    "link": entry.link,
                    "published": published.isoformat(),
                    "summary": cleaned,
                    "id": entry.id if "id" in entry else entry_id,
                    "category": category,
                    "image": entry.enclosures[0].href if entry.enclosures else ""
                }

    filtered = {
        k: v for k, v in cache.items()
        if datetime.fromisoformat(v["published"]).replace(tzinfo=timezone.utc) >= cutoff
    }
    save_cache(filtered)
    return filtered

def generate_feed(entries):
    fg = FeedGenerator()
    fg.id('fd736935-55ce-469a-bedb-fb4111f9e7b1')
    fg.title('Newsletter Przegląd Sportowy')
    fg.description('Zbiorczy RSS z Przeglądu Sportowego')
    fg.link(href='https://przegladsportowy.onet.pl/', rel='alternate')
    fg.logo('https://ocdn.eu/przegladsportowy/static/logo-ps-feed.png')
    fg.language('pl')
    fg.author(name='PrzegladSportowy.onet.pl')

    for item in sorted(entries.values(), key=lambda x: x['published'], reverse=True):
        fe = fg.add_entry()
        fe.id(item["id"])
        fe.title(item["title"])
        fe.link(href=item["link"], rel='alternate', type='text/html')
        pub_dt = datetime.fromisoformat(item["published"]).replace(tzinfo=timezone.utc)
        fe.published(pub_dt)
        fe.summary(item["summary"], type='html')
        if item["image"]:
            fe.enclosure(url=item["image"], type="image/jpeg", length="0")
        fe.category(term=item["category"])

    rss_content = fg.rss_str(pretty=True).decode('utf-8')

    # Usuń istniejące <?xml ... ?> jeśli jest
    rss_content = re.sub(r'^<\?xml[^>]+\?>', '', rss_content).lstrip()

    # Nasza poprawna deklaracja XML z podwójnymi cudzysłowami
    xml_declaration_line = '<?xml version="1.0" encoding="UTF-8"?>\n'

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_declaration_line)
        f.write(rss_content)




def main():
    entries = update_cache()
    os.makedirs('docs', exist_ok=True)
    generate_feed(entries)

if __name__ == '__main__':
    main()
