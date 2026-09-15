# The Polite Scraper

**FlyRank Internship — Backend Track — Week 5 — Assignment A9**

A small Python scraper that collects book data from the public **Books to Scrape** practice sandbox and turns messy HTML into clean, validated JSON.

The pipeline is:

**fetch → extract → normalize → validate → store → report**

---

## Target Classification

### Target

**Books to Scrape**

Books to Scrape is a public practice sandbox built for people to learn and practise web scraping.

### Scope

This scraper processes **only the first three catalogue pages**, discovering **60 unique book pages** in total.

The scraper does not hardcode the 60 book links. It follows the catalogue's actual `next` links from page 1 to page 2 to page 3.

### Data Collected

For each book, the scraper collects these eight raw fields:

- `title`
- `product_url`
- `price_text`
- `availability_text`
- `rating_text`
- `description`
- `source_page`
- `fetched_at`

The price is also normalized into:

- `price_gbp`

For example:

    price_text: "£51.77"
    price_gbp: 51.77

---

## Robots Check

I requested:

    https://books.toscrape.com/robots.txt

The response was **404 Not Found**, so **no robots file was found**.

A missing robots file is not treated as permission to scrape other websites.

This assignment specifically uses Books to Scrape because it is a public practice sandbox intended for scraping practice.

### Why This Target Is Appropriate

Books to Scrape is the practice sandbox specified for this assignment.

The scraper stays within the required first three catalogue pages and uses polite fetching practices such as:

- an identifying user-agent
- request timeouts
- caching
- a delay between real requests
- limited scraping scope
- retry handling for temporary failures

> **I will not reuse this code on another site without checking its rules and terms first.**

---

## Python Lane

This implementation uses the Python lane:

- Python 3.10+
- Requests
- Beautiful Soup
- Pydantic
- Python `json` module

### Installation

From the `scrape` directory, install the required dependencies:

    pip install requests beautifulsoup4 pydantic

### Run

From the `scrape` directory, run:

    python src/main.py

The scraper generates:

    output/
    ├── books.json
    ├── errors.json
    └── run-report.json

The `cache/` directory stores downloaded HTML during development so repeated runs can use cached copies instead of repeatedly requesting the website.

---

## Record Schema

Every valid record is checked using a Pydantic schema.

### Example Record

    {
      "title": "A Light in the Attic",
      "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
      "price_text": "£51.77",
      "price_gbp": 51.77,
      "availability_text": "In stock (22 available)",
      "rating_text": "Three",
      "description": "...",
      "source_page": "https://books.toscrape.com/catalogue/page-1.html",
      "fetched_at": "2026-09-15T18:10:50.582032+00:00"
    }

### Field Rules

| Field | Type | Required |
|---|---|---|
| `title` | string | Yes |
| `product_url` | HTTPS URL | Yes |
| `price_text` | string | Yes |
| `price_gbp` | number | Yes |
| `availability_text` | string | Yes |
| `rating_text` | string | Yes |
| `description` | string or null | No |
| `source_page` | HTTPS URL | Yes |
| `fetched_at` | string | Yes |

Records are normalized and validated before being added to `books.json`.

If a record fails normalization or validation, it is recorded in `errors.json`.

---

## Politeness Rules

The scraper follows these rules for real requests:

- Uses an identifying user-agent.
- Uses a **5-second request timeout**.
- Requires HTTP `200` for a successful fetch.
- Waits at least **0.5 seconds between real requests**.
- Cached pages do not require a delay because they do not create a network request.
- Follows the site's actual catalogue `next` links.
- Deduplicates discovered book URLs.
- Retries a timeout or HTTP `5xx` server error once after waiting.
- Does **not** retry HTTP `403` or `404`.
- Processes each book page independently so one failed page does not stop the complete run.

### User-Agent

    FlyRankInternship-A9/1.0 (+https://github.com/HR-Fatheen/Task-API)

---

## Caching

Downloaded pages are stored locally in the `cache/` directory.

The cache contains the downloaded catalogue and book HTML pages used during development.

After the initial download, development runs can use cached copies instead of repeatedly requesting the website.

The cache directory is ignored by Git and is not published to the repository.

---

## Failure Handling

Each book page is processed independently.

Temporary failures such as request timeouts and HTTP `5xx` server errors are retried once after waiting.

HTTP `403` and `404` responses are not retried.

If a page still fails, the failure is recorded and the scraper continues processing the remaining books.

### Fake URL Test

A deliberate failure test was performed against:

    https://books.toscrape.com/this-page-does-not-exist-999999.html

The scraper correctly produced:

    RuntimeError: HTTP 404 for https://books.toscrape.com/this-page-does-not-exist-999999.html

The `404` was not retried, which is the expected behavior.

---

## Run Report

Each run generates:

    output/run-report.json

The report records:

- run start time
- duration
- catalogue pages processed
- detail pages processed
- number of network requests
- cache hits
- valid records
- invalid records
- failed pages

### Example Successful Cached Run

    {
      "started_at": "2026-09-15T18:14:58.831923+00:00",
      "duration_seconds": 1.66,
      "catalogue_pages": 3,
      "detail_pages": 60,
      "requests": 0,
      "cache_hits": 63,
      "valid_records": 60,
      "invalid_records": 0,
      "failed_pages": []
    }

The run produced:

    catalogue_pages=3
    detail_pages=60
    valid_records=60
    invalid_records=0
    failed_pages=0
    cache_hits=63
    requests=0
    duration_seconds=1.66

The `0` network requests in this particular run is expected because all 63 required pages were already cached.

---

## Stage Checkpoints

### Stage 0 — Target Classification

The following checks were completed:

- Target classified as Books to Scrape.
- Scope limited to the first three catalogue pages.
- `robots.txt` checked.
- `robots.txt` returned 404 Not Found.
- Required warning about reusing the scraper on other sites documented.

### Stage 1 — Fetch and Cache HTML

The following checks were completed:

- Catalogue page 1 fetched successfully.
- HTML saved to `cache/catalogue-page-1.html`.
- A subsequent development run produced a cache hit.

### Stage 2 — Discover Three Catalogue Pages

The scraper followed the catalogue's actual `next` links.

Checkpoint:

    catalogue_pages=3
    discovered=60
    unique_urls=60

The 60 book URLs were discovered dynamically rather than hardcoded.

### Stage 3 — Extract Book Details

The following checks were completed:

- 60 book detail pages processed.
- Each raw record contains the required eight fields.
- `source_page` is retained for provenance.
- `fetched_at` records when the page was processed.

### Stage 4 — Validate Normalized Records

The scraper normalizes the price and validates every record with Pydantic.

Checkpoint:

    records: 60
    errors: 0

Example:

    price_text = £51.77
    price_gbp  = 51.77

All 60 records passed validation.

### Stage 5 — Survive Failures and Report the Run

Successful run:

    valid_records=60
    invalid_records=0
    failed_pages=0

A deliberate fake `404` URL was also tested and correctly failed without retrying.

### Stage 6 — Publish Scraper Evidence

The scraper documentation, source code, run evidence, and Git history are prepared for final repository publication.

Generated cache files remain ignored by Git.

---

## Why No Browser Was Needed

A browser is not required for this assignment because the required book information is already present in the HTML returned by the server.

The scraper can retrieve and parse the HTML directly using Requests and Beautiful Soup.

Using a browser would add unnecessary complexity for this particular task without providing functionality that the scraper needs.

---

## Limitation

This scraper is intentionally limited to the **first three catalogue pages and 60 books** required by the assignment.

It is an assignment-focused scraper rather than a general-purpose crawler.

It does not attempt to crawl the entire website or support arbitrary website structures.

---

## Ethics Note

When scraping other websites:

- Check the site's rules and terms before collecting data.
- Use an official API when one is available.
- Identify the scraper honestly.
- Use reasonable request rates.
- Avoid unnecessary traffic.
- Collect only the data that is actually needed.
- Never bypass authentication, paywalls, access controls, or other restrictions.

This implementation is specifically intended for the Books to Scrape practice sandbox.

---

## Project Structure

The A9 scraper uses the following structure:

    Assignment 1/
    └── scrape/
        ├── cache/                  # Downloaded HTML; ignored by Git
        ├── output/                 # Generated JSON output; ignored by Git
        ├── src/
        │   └── main.py             # Scraper implementation
        ├── .gitignore
        └── README.md               # A9 documentation

---

## Git History

The assignment was developed incrementally through meaningful stage commits:

1. `Stage 0: classify scraping target`
2. `Stage 1: fetch and cache HTML`
3. `Stage 2: discover three catalogue pages`
4. `Stage 3: extract book details`
5. `Stage 4: validate normalized records`
6. `Stage 5: survive failures, report the run`

The Stage 6 commit will be created after the final documentation and repository checks are complete.

---

## Status

**Assignment A9 — Stages 0–5 completed.**

The scraper has successfully:

- discovered 60 unique books
- processed 60 detail pages
- normalized prices
- validated records with Pydantic
- generated valid output
- handled a deliberate `404` failure
- generated a run report
- maintained a polite request strategy

**Stage 6 is ready for final repository publication.**