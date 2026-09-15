from pathlib import Path
from time import monotonic, sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
CATALOGUE_PAGE_1_URL = urljoin(BASE_URL, "catalogue/page-1.html")

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": (
        "FlyRankInternship-A9/1.0 "
        "(+https://github.com/HR-Fatheen/Task-API)"
    )
}

TIMEOUT = 5
REQUEST_DELAY = 0.5

last_request_time = 0.0


def fetch_page(url, cache_file, verbose=False):
    """
    Fetch a page or use the cached copy if it already exists.
    Real requests are separated by at least 0.5 seconds.
    """

    global last_request_time

    cache_path = CACHE_DIR / cache_file

    if cache_path.exists():
        if verbose:
            print(f"CACHE HIT: {cache_path}")
        return cache_path.read_text(encoding="utf-8")

    elapsed = monotonic() - last_request_time

    if elapsed < REQUEST_DELAY:
        sleep(REQUEST_DELAY - elapsed)

    if verbose:
        print(f"FETCH: {url}")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=TIMEOUT,
    )

    last_request_time = monotonic()

    if response.status_code != 200:
        raise RuntimeError(
            f"HTTP {response.status_code} for {url}"
        )

    # Books to Scrape serves UTF-8 content.
    response.encoding = "utf-8"

    html = response.text

    cache_path.write_text(
        html,
        encoding="utf-8",
    )

    if verbose:
        print(f"Response size: {len(html)} bytes")
        print(f"Saved: {cache_path}")

    return html


def discover_books():
    """
    Follow the catalogue's actual next links for exactly
    three catalogue pages and collect unique book URLs.
    """

    current_url = CATALOGUE_PAGE_1_URL
    book_urls = []
    source_pages = {}

    for page_number in range(1, 4):
        cache_file = f"catalogue-page-{page_number}.html"

        html = fetch_page(
            current_url,
            cache_file,
            verbose=True,
        )

        soup = BeautifulSoup(html, "html.parser")

        for article in soup.select("article.product_pod"):
            link = article.select_one("h3 a")

            if not link or not link.get("href"):
                continue

            product_url = urljoin(
                BASE_URL,
                link["href"],
            )

            if product_url not in book_urls:
                book_urls.append(product_url)
                source_pages[product_url] = current_url

        if page_number < 3:
            next_link = soup.select_one("li.next a")

            if not next_link or not next_link.get("href"):
                break

            current_url = urljoin(
                current_url,
                next_link["href"],
            )

    print(
        f"catalogue_pages=3, "
        f"discovered={len(book_urls)}, "
        f"unique_urls={len(set(book_urls))}"
    )

    return book_urls, source_pages


def clean_price_text(text):
    """
    Fix common mojibake caused by incorrect character decoding.
    """

    if not text:
        return None

    return (
        text
        .replace("Â£", "£")
        .replace("\xa0", " ")
        .strip()
    )


def clean_description(text):
    """
    Normalize whitespace and remove accidental repeated
    description content if the same opening appears twice.
    """

    if not text:
        return None

    text = " ".join(text.split())

    # Some cached pages may contain the description twice.
    # Detect a repeated opening section and keep the first copy.
    if len(text) > 240:
        prefix = text[:120]
        repeat_index = text.find(prefix, 120)

        if repeat_index != -1:
            text = text[:repeat_index].strip()

    return text


def extract_book(book_url, source_page, index):
    """
    Extract the eight raw fields required by Assignment A9.
    """

    cache_file = f"book-{index:03d}.html"

    html = fetch_page(
        book_url,
        cache_file,
        verbose=False,
    )

    soup = BeautifulSoup(html, "html.parser")

    title_element = soup.select_one("h1")
    price_element = soup.select_one(".price_color")
    availability_element = soup.select_one(".availability")
    rating_element = soup.select_one(".star-rating")

    description_element = None

    description_heading = soup.select_one("#product_description")

    if description_heading:
        description_element = description_heading.find_next_sibling("p")

    title = (
        title_element.get_text(" ", strip=True)
        if title_element
        else None
    )

    price_text = (
        clean_price_text(
            price_element.get_text(" ", strip=True)
        )
        if price_element
        else None
    )

    availability_text = (
        availability_element.get_text(" ", strip=True)
        if availability_element
        else None
    )

    rating_text = None

    if rating_element:
        classes = rating_element.get("class", [])

        rating_classes = [
            value
            for value in classes
            if value != "star-rating"
        ]

        if rating_classes:
            rating_text = rating_classes[0]

    description = (
        clean_description(
            description_element.get_text(" ", strip=True)
        )
        if description_element
        else None
    )

    from datetime import datetime, timezone

    fetched_at = datetime.now(timezone.utc).isoformat()

    return {
        "title": title,
        "product_url": book_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at,
    }


def main():
    book_urls, source_pages = discover_books()

    records = []

    for index, book_url in enumerate(book_urls, start=1):
        print(f"Processing books: {index}/{len(book_urls)}")

        record = extract_book(
            book_url,
            source_pages[book_url],
            index,
        )

        records.append(record)

    print(f"detail_pages={len(records)}")

    if records:
        print("\nFirst raw record:")
        print(records[0])


if __name__ == "__main__":
    main()