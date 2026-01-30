import feedparser
import json
from datetime import datetime, timedelta, timezone
import re
import requests
from feedgen.feed import FeedGenerator
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
    "https://przegladsportowy.onet.pl/kajakarstwo.feed",
]

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
    "kajakarstwo": "Kajakarstwo",
}


def pretty_category(slug: str) -> str:
    if slug in CATEGORY_MAP:
        return CATEGORY_MAP[slug]
    return slug.replace("-", " ").replace("/", " / ").title()


CACHE_FILE = "cache.json"
OUTPUT_FILE = "docs/rss.xml"
RETENTION_DAYS = 7


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    for img in soup.find_all("img"):
        img.decompose()
    return unescape(soup.get_text(strip=True))


def get_category_from_url(url: str) -> str:
    match = re.search(r"onet\.pl/(.*?)\.feed", url)
    return match.group(1) if match else "inne"


def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache: dict) -> None:
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def update_cache() -> dict:
    print("🔧 Wchodzę do update_cache()")
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=RETENTION_DAYS)
    cache = load_cache()

    # MIGRACJA: slug -> ładna nazwa + zachowanie slug
    changed = False
    for _, v in list(cache.items()):
        cat_slug = v.get("category_slug") or v.get("category")
        if cat_slug:
            nice = pretty_category(cat_slug)
            if v.get("category") != nice:
                v["category"] = nice
                v["category_slug"] = cat_slug
                changed = True
    if changed:
        save_cache(cache)

    headers = {
        "User-Agent": "newsletter-ps-feed/1.0 (+https://github.com/arkadiuszgondek/newsletter-ps-feed)"
    }

    print("➡️ Początek aktualizacji cache")

    for url in FEED_URLS:
        print(f"🔗 Przetwarzam: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=30)
            print(
                "status:", response.status_code,
                "content-type:", response.headers.get("Content-Type"),
                "bytes:", len(response.content)
            )
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Błąd pobierania {url}: {e}")
            continue

        feed = feedparser.parse(response.content)
        soup = BeautifulSoup(response.content, "xml")

        # Atom: <entry>, RSS 2.0: <item>
        entries_raw = soup.find_all("entry")
        raw_mode = "entry"
        if not entries_raw:
            entries_raw = soup.find_all("item")
            raw_mode = "item"

        if entries_raw:
            iterable = zip(entries_raw, feed.entries)
        else:
            iterable = [(None, e) for e in feed.entries]
            raw_mode = "none"

        print(
            "len(feed.entries):", len(feed.entries),
            "raw_mode:", raw_mode,
            "raw_count:", len(entries_raw),
        )

        category = get_category_from_url(url)

        for raw_entry, parsed_entry in iterable:
            # published / updated
            dt_struct = getattr(parsed_entry, "published_parsed", None) or getattr(parsed_entry, "updated_parsed", None)
            if not dt_struct:
                continue
            published = datetime(*dt_struct[:6], tzinfo=timezone.utc)

            entry_id = getattr(parsed_entry, "id", None) or getattr(parsed_entry, "guid", None) or parsed_entry.link

            # dedup po linku
            if any(parsed_entry.link == v.get("link") for v in cache.values()):
                continue

            # jeśli nowy lub nowszy niż poprzednio zapisany
            if entry_id not in cache or published > datetime.fromisoformat(cache[entry_id]["published"]):
                if raw_entry:
                    if raw_mode == "entry":
                        summary_tag = raw_entry.find("summary")
                        summary_raw = summary_tag.decode_contents() if summary_tag else ""
                    elif raw_mode == "item":
                        desc_tag = raw_entry.find("description")
                        summary_raw = desc_tag.decode_contents() if desc_tag else ""
                    else:
                        summary_raw = ""
                else:
                    summary_raw = getattr(parsed_entry, "summary", "") or getattr(parsed_entry, "description", "") or ""

                cache[entry_id] = {
                    "title": getattr(parsed_entry, "title", "").strip(),
                    "link": parsed_entry.link,
                    "published": published.isoformat(),
                    "summary": summary_raw or "",
                    "id": entry_id,
                    "category": pretty_category(category),
                    "category_slug": category,
                    "image": parsed_entry.enclosures[0].href if getattr(parsed_entry, "enclosures", None) else "",
                }

    # filtr ostatnich 7 dni
    filtered = {
        k: v for k, v in cache.items()
        if datetime.fromisoformat(v["published"]).replace(tzinfo=timezone.utc) >= cutoff
    }

    print(f"✅ Zapisuję {len(filtered)} wpisów do cache.json")
    save_cache(filtered)
    return filtered


def generate_feed(entries: dict) -> None:
    fg = FeedGenerator()
    fg.id("fd736935-55ce-469a-bedb-fb4111f9e7b1")
    fg.title("Newsletter Przegląd Sportowy")
    fg.description("Zbiorczy RSS z Przeglądu Sportowego")
    fg.link(href="https://przegladsportowy.onet.pl/", rel="alternate")
    fg.logo("https://ocdn.eu/przegladsportowy/static/logo-ps-feed.png")
    fg.language("pl")
    fg.author(name="PrzegladSportowy.onet.pl")

    used_ids = set()

    for item in sorted(entries.values(), key=lambda x: x["published"], reverse=True):
        if item["id"] in used_ids:
            continue
        used_ids.add(item["id"])

        fe = fg.add_entry()
        fe.id(item["id"])
        fe.title(item["title"])
        fe.link(href=item["link"], rel="alternate", type="text/html")

        pub_dt = datetime.fromisoformat(item["published"]).replace(tzinfo=timezone.utc)
        fe.published(pub_dt)

        # Uwaga: feedgen nie lubi "surowego" HTML bez escapingu — więc trzymamy XML-safe
        fe.description(escape(item.get("summary") or ""))

        if item.get("image"):
            fe.enclosure(url=item["image"], type="image/jpeg", length="0")

        fe.category(term=item.get("category") or "Inne")

    rss_content = fg.rss_str(pretty=True).decode("utf-8")

    # usuń istniejące <?xml ... ?> jeśli jest
    rss_content = re.sub(r'^<\?xml[^>]+\?>', "", rss_content).lstrip()

    xml_declaration_line = '<?xml version="1.0" encoding="UTF-8"?>\n'

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(xml_declaration_line)
        f.write(rss_content)


def main() -> None:
    entries = update_cache()
    generate_feed(entries)


if __name__ == "__main__":
    main()
