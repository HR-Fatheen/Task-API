from pathlib import Path
from time import monotonic, sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/HR-Fatheen/Task-API)"
}

TIMEOUT = 5
MIN_REQUEST_INTERVAL = 0.5

last_request_time = None


def fetch_page(url, cache_file):
    global last_request_time

    if cache_file.exists():
        html = cache_file.read_text(encoding="utf-8")
        print(f"CACHE HIT: {cache_file}")
        return html

    if last_request_time is not None:
        elapsed = monotonic() - last_request_time
        if elapsed < MIN_REQUEST_INTERVAL:
            sleep(MIN_REQUEST_INTERVAL - elapsed)

    print(f"FETCH: {url}")

    try:
        last_request_time = monotonic()

        response = requests.get(
            url,
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
    cache_file.write_text(html, encoding="utf-8")

    print(f"Response size: {len(html)} bytes")
    print(f"Saved: {cache_file}")

    return html


def discover_books():
    current_url = BASE_URL
    discovered_urls = set()
    catalogue_pages = 0

    while catalogue_pages < 3:
        page_number = catalogue_pages + 1

        if page_number == 1:
            cache_file = CACHE_DIR / "catalogue-page-1.html"
        else:
            cache_file = CACHE_DIR / f"catalogue-page-{page_number}.html"

        html = fetch_page(current_url, cache_file)

        if html is None:
            break

        soup = BeautifulSoup(html, "html.parser")

        for link in soup.select("article.product_pod h3 a"):
            product_url = urljoin(current_url, link.get("href"))
            discovered_urls.add(product_url)

        catalogue_pages += 1

        if catalogue_pages == 3:
            break

        next_link = soup.select_one("li.next a")

        if not next_link:
            print("NEXT LINK NOT FOUND")
            break

        current_url = urljoin(current_url, next_link.get("href"))

    print(f"catalogue_pages={catalogue_pages}, discovered={len(discovered_urls)}, unique_urls={len(discovered_urls)}")

    return discovered_urls


if __name__ == "__main__":
    discover_books()