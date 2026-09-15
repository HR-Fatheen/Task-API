from pathlib import Path

import requests


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/HR-Fatheen/Task-API)"
}

TIMEOUT = 5


def fetch_catalogue_page():
    if CACHE_FILE.exists():
        html = CACHE_FILE.read_text(encoding="utf-8")
        print(f"CACHE HIT: {CACHE_FILE}")
        print(f"Response size: {len(html)} bytes")
        return html

    print(f"FETCH: {BASE_URL}")

    try:
        response = requests.get(
            BASE_URL,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        print(f"FETCH FAILED: {exc}")
        return None

    if response.status_code != 200:
        print(f"FETCH FAILED: HTTP {response.status_code}")
        return None

    html = response.text

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(html, encoding="utf-8")

    print(f"Response size: {len(html)} bytes")
    print(f"Saved: {CACHE_FILE}")

    return html


if __name__ == "__main__":
    fetch_catalogue_page()