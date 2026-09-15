from datetime import datetime, timezone
import json
import re
from pathlib import Path
from time import monotonic, sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl, ValidationError


BASE_URL = "https://books.toscrape.com/"
CATALOGUE_PAGE_1_URL = urljoin(BASE_URL, "catalogue/page-1.html")

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": (
        "FlyRankInternship-A9/1.0 "
        "(+https://github.com/HR-Fatheen/Task-API)"
    )
}

TIMEOUT = 5
REQUEST_DELAY = 0.5

last_request_time = 0.0

stats = {
    "requests": 0,
    "cache_hits": 0,
    "catalogue_pages": 0,
    "detail_pages": 0,
}


class Book(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None
    source_page: HttpUrl
    fetched_at: str


def fetch_page(url, cache_file, verbose=False):
    """
    Fetch a page or use the cached copy if it already exists.

    Temporary failures are retried once.
    403 and 404 responses are not retried.
    Real requests are separated by at least 0.5 seconds.
    """

    global last_request_time

    cache_path = CACHE_DIR / cache_file

    if cache_path.exists():
        stats["cache_hits"] += 1

        if verbose:
            print(f"CACHE HIT: {cache_path}")

        return cache_path.read_text(encoding="utf-8")

    for attempt in range(2):
        elapsed = monotonic() - last_request_time

        if elapsed < REQUEST_DELAY:
            sleep(REQUEST_DELAY - elapsed)

        if verbose:
            print(f"FETCH: {url}")

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT,
            )

            last_request_time = monotonic()
            stats["requests"] += 1

        except requests.RequestException as exc:
            last_request_time = monotonic()
            stats["requests"] += 1

            if attempt == 0:
                print(f"Temporary request failure, retrying: {url}")
                sleep(1)
                continue

            raise RuntimeError(
                f"Request failed for {url}: {exc}"
            ) from exc

        if response.status_code == 200:
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

        if response.status_code in (403, 404):
            raise RuntimeError(
                f"HTTP {response.status_code} for {url}"
            )

        if 500 <= response.status_code <= 599:
            if attempt == 0:
                print(
                    f"Server error HTTP {response.status_code}, "
                    f"retrying: {url}"
                )
                sleep(1)
                continue

            raise RuntimeError(
                f"HTTP {response.status_code} for {url}"
            )

        raise RuntimeError(
            f"HTTP {response.status_code} for {url}"
        )

    raise RuntimeError(f"Failed to fetch {url}")


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

        stats["catalogue_pages"] += 1

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
        f"catalogue_pages={stats['catalogue_pages']}, "
        f"discovered={len(book_urls)}, "
        f"unique_urls={len(set(book_urls))}"
    )

    return book_urls, source_pages


def clean_price_text(text):
    if not text:
        return None

    text = text.replace("\xa0", " ").strip()

    match = re.search(r"\d+(?:[.,]\d+)?", text)

    if match:
        number = match.group(0).replace(",", ".")
        return f"£{number}"

    return text


def normalize_price(price_text):
    if not price_text:
        raise ValueError("Missing price")

    cleaned = (
        price_text
        .replace("£", "")
        .replace(",", "")
        .strip()
    )

    return float(cleaned)


def clean_description(text):
    if not text:
        return None

    text = " ".join(text.split())

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

    stats["detail_pages"] += 1

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


def validate_and_normalize(raw_record):
    normalized = raw_record.copy()

    normalized["price_gbp"] = normalize_price(
        raw_record["price_text"]
    )

    return Book.model_validate(normalized)


def save_json(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


def main():
    started_at = datetime.now(timezone.utc)
    start_monotonic = monotonic()

    valid_books = []
    errors = []
    failed_pages = []

    try:
        book_urls, source_pages = discover_books()
    except Exception as exc:
        book_urls = []
        source_pages = {}

        errors.append(
            {
                "stage": "catalogue",
                "error": str(exc),
            }
        )

    for index, book_url in enumerate(book_urls, start=1):
        print(f"Processing books: {index}/{len(book_urls)}")

        try:
            raw_record = extract_book(
                book_url,
                source_pages[book_url],
                index,
            )

            book = validate_and_normalize(raw_record)

            valid_books.append(
                book.model_dump(mode="json")
            )

        except (ValueError, ValidationError, RuntimeError) as exc:
            errors.append(
                {
                    "product_url": book_url,
                    "error": str(exc),
                }
            )

            failed_pages.append(
                {
                    "product_url": book_url,
                    "error": str(exc),
                }
            )

            print(f"FAILED: {book_url}")

    save_json(
        OUTPUT_DIR / "books.json",
        valid_books,
    )

    save_json(
        OUTPUT_DIR / "errors.json",
        errors,
    )

    duration_seconds = round(
        monotonic() - start_monotonic,
        2,
    )

    report = {
        "started_at": started_at.isoformat(),
        "duration_seconds": duration_seconds,
        "catalogue_pages": stats["catalogue_pages"],
        "detail_pages": stats["detail_pages"],
        "requests": stats["requests"],
        "cache_hits": stats["cache_hits"],
        "valid_records": len(valid_books),
        "invalid_records": len(errors),
        "failed_pages": failed_pages,
    }

    save_json(
        OUTPUT_DIR / "run-report.json",
        report,
    )

    print()
    print(f"catalogue_pages={stats['catalogue_pages']}")
    print(f"detail_pages={stats['detail_pages']}")
    print(f"valid_records={len(valid_books)}")
    print(f"invalid_records={len(errors)}")
    print(f"failed_pages={len(failed_pages)}")
    print(f"cache_hits={stats['cache_hits']}")
    print(f"requests={stats['requests']}")
    print(f"duration_seconds={duration_seconds}")
    print(f"Saved: {OUTPUT_DIR / 'books.json'}")
    print(f"Saved: {OUTPUT_DIR / 'errors.json'}")
    print(f"Saved: {OUTPUT_DIR / 'run-report.json'}")


if __name__ == "__main__":
    main()