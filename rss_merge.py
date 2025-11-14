import feedparser
import json
from datetime import datetime, timedelta, timezone
import re
import requests
from feedgen.feed import FeedGenerator
import hashlib
import os
from html import unescape, escape
from bs4 import BeautifulSoup

FEED_URLS = [
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
    "https://przegladsportowy.onet.pl/sporty-lotnicze.feed",
    "https://przegladsportowy.onet.pl/szachy.feed",
    "https://przegladsportowy.onet.pl/plebiscyt-przegladu-sportowego.feed",
    "https://przegladsportowy.onet.pl/kajakarstwo.feed"
]
# Mapowanie slugów z URL na ładne nazwy z polskimi znakami
CATEGORY_MAP = {
    "pilka-nozna": "Piłka nożna",
    "tenis": "Tenis",
    "siatkowka": "Siatkówka",
    "koszykowka": "Koszykówka",
    "zuzel": "Żużel",
    "alpinizm": "Alpinizm",
    "ofsajd": "Ofsajd",
    "czas-na-bieganie": "Czas na bieganie",
    "esportmania": "Esportmania",
    "futbol-amerykanski": "Futbol amerykański",
    "hokej-na-lodzie": "Hokej na lodzie",
    "jezdziectwo": "Jeździectwo",
    "kolarstwo": "Kolarstwo",
    "paraolimpiada": "Paraolimpiada",
    "snooker": "Snooker",
    "badminton": "Badminton",
    "sporty-zimowe/biegi-narciarskie": "Biegi narciarskie",
    "felietony": "Felietony",
    "pilka-nozna/futsal": "Futsal",
    "hokej-na-trawie": "Hokej na trawie",
    "judo": "Judo",
    "lekkoatletyka": "Lekkoatletyka",
    "plywanie": "Pływanie",
    "rugby": "Rugby",
    "sport-akademicki": "Sport akademicki",
    "baseball": "Baseball",
    "boks": "Boks",
    "fitness-i-porady": "Fitness i porady",
    "gimnastyka": "Gimnastyka",
    "lucznictwo": "Łucznictwo",
    "igrzyska-olimpijskie": "Igrzyska olimpijskie",
    "mma": "MMA",
    "piecioboj-nowoczesny": "Pięciobój nowoczesny",
    "sporty-zimowe/biathlon": "Biathlon",
    "drift-masters": "Drift Masters",
    "formula-1": "Formuła 1",
    "golf": "Golf",
    "inne-sporty": "Inne sporty",
    "sporty-zimowe/lyzwiarstwo": "Łyżwiarstwo",
    "motorowe": "Motorowe",
    "pilka-reczna": "Piłka ręczna",
    "podnoszenie-ciezarow": "Podnoszenie ciężarów",
    "sporty-zimowe/skoki-narciarskie": "Skoki narciarskie",
    "sporty-lotnicze": "Sporty lotnicze",
    "szachy": "Szachy",
    "plebiscyt-przegladu-sportowego": "Plebiscyt Przeglądu Sportowego",
    "kajakarstwo": "Kajakarstwo"
}

def pretty_category(slug: str) -> str:
    # Zwróć ładną nazwę; fallback: zamień '-' na spacje i tytułuj
    if slug in CATEGORY_MAP:
        return CATEGORY_MAP[slug]
    # dla ścieżek z '/' sformatuj czytelnie
    return slug.replace('-', ' ').replace('/', ' / ').title()

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

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def update_cache():
    print("🔧 Wchodzę do update_cache()")
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=RETENTION_DAYS)
    cache = load_cache()

    # MIGRACJA: podmień kategorie w już zapisanych wpisach (slug -> ładna nazwa)
    changed = False
    for k, v in list(cache.items()):
        cat_slug = v.get("category_slug") or v.get("category")
        if cat_slug:
            nice = pretty_category(cat_slug)
            if v.get("category") != nice:
                v["category"] = nice            # ładna nazwa z ogonkami
                v["category_slug"] = cat_slug   # oryginalny slug
                changed = True
    if changed:
        save_cache(cache)

    print("➡️ Początek aktualizacji cache")

    for url in FEED_URLS:
        print(f"🔗 Przetwarzam: {url}")
        response = requests.get(url)
        feed = feedparser.parse(response.content)
        soup = BeautifulSoup(response.content, 'xml')
        entries_raw = soup.find_all('entry')
        category = get_category_from_url(url)  # slug z URL-a

        for raw_entry, parsed_entry in zip(entries_raw, feed.entries):
            published = datetime(*parsed_entry.published_parsed[:6])  # bez TZ – wyrównamy przy zapisie/porównaniu
            entry_id = parsed_entry.id if "id" in parsed_entry else parsed_entry.link

            # dedup po linku
            if any(parsed_entry.link == v["link"] for v in cache.values()):
                print(f"⏭️ Pomijam duplikat: {parsed_entry.link}")
                continue

            if entry_id not in cache or published > datetime.fromisoformat(cache[entry_id]["published"]):
                summary_tag = raw_entry.find('summary')
                summary_raw = summary_tag.decode_contents() if summary_tag else ""

                print(f"📦 Summary dla {parsed_entry.link}:\n{summary_raw}\n---")

                cat_slug = category
                cache[entry_id] = {
                    "title": parsed_entry.title,
                    "link": parsed_entry.link,
                    "published": published.isoformat(),
                    "summary": summary_raw,
                    "id": entry_id,
                    "category": pretty_category(cat_slug),   # ładna nazwa z ogonkami
                    "category_slug": cat_slug,               # zachowujemy slug
                    "image": parsed_entry.enclosures[0].href if parsed_entry.enclosures else ""
                }

    # filtr 7 dni
    filtered = {
        k: v for k, v in cache.items()
        if datetime.fromisoformat(v["published"]).replace(tzinfo=timezone.utc) >= cutoff
    }

    print(f"✅ Zapisuję {len(filtered)} wpisów do cache.json")
    print("💾 Zapisuję cache do pliku:", CACHE_FILE)
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

    used_ids = set()

    for item in sorted(entries.values(), key=lambda x: x['published'], reverse=True):
        if item["id"] in used_ids:
            continue  # pomiń duplikat GUID
        used_ids.add(item["id"])

        fe = fg.add_entry()
        fe.id(item["id"])
        fe.title(item["title"])
        fe.link(href=item["link"], rel='alternate', type='text/html')
        pub_dt = datetime.fromisoformat(item["published"]).replace(tzinfo=timezone.utc)
        fe.published(pub_dt)

        # ✅ Właściwa linia — dekodujemy HTML przed wstawieniem
        fe.description(escape(item["summary"] or ""))

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
