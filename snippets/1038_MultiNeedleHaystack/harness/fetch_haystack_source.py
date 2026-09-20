import json
import os
import datetime
import urllib.parse
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "..", "data", "haystack_source")

API_URL = "https://hu.wikipedia.org/w/api.php"

# Wikimedia API-etikett: azonosító User-Agent nélkül 403-at ad vissza.
HEADERS = {
    "User-Agent": "MultiNeedleHaystack-MIEsettanulmany/1.0 (https://github.com/bmeaut/snippets; oktatasi celu kutatas)"
}


def fetch_article(title):
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": 1,
        "format": "json",
        "redirects": 1,
        "titles": title,
    }
    resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    if "missing" in page:
        raise ValueError(f"A(z) '{title}' című cikk nem található a hu.wikipedia.org-on.")
    return page["title"], page["extract"]


def main():
    with open(os.path.join(BASE, "wiki_articles.json"), encoding="utf-8") as f:
        config = json.load(f)

    os.makedirs(OUT_DIR, exist_ok=True)
    fetch_date = datetime.date.today().isoformat()

    manifest = []
    for title in config["titles"]:
        canonical_title, text = fetch_article(title)
        slug = canonical_title.replace(" ", "_").replace("/", "_")
        txt_path = os.path.join(OUT_DIR, f"{slug}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        url = "https://hu.wikipedia.org/wiki/" + urllib.parse.quote(canonical_title.replace(" ", "_"))
        entry = {
            "title": canonical_title,
            "url": url,
            "license": config["license"],
            "fetched": fetch_date,
            "chars": len(text),
            "file": os.path.relpath(txt_path, os.path.join(BASE, "..")),
        }
        manifest.append(entry)
        print(f"[OK] {canonical_title}: {len(text)} karakter -> {txt_path}")

    manifest_path = os.path.join(OUT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    total_chars = sum(e["chars"] for e in manifest)
    print(f"\nÖsszesen {len(manifest)} cikk, {total_chars} karakter.")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
