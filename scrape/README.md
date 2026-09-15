# The Polite Scraper

FlyRank Internship - Backend Track - Week 5 - Assignment A9

A small Python scraper that collects book data from the public Books to Scrape practice sandbox and turns messy HTML into clean, validated JSON.

## Target Classification

### Target

**Books to Scrape**

Books to Scrape is a public practice sandbox built for people to learn and practise web scraping.

### Scope

This scraper will collect data from **only the first three catalogue pages**, discovering **60 unique book pages** in total.

The scraper will not hardcode the 60 book links. It will follow the catalogue's own next-page links from page 1 to page 2 to page 3.

### Data Collected

For each book, the scraper will collect:

- `title`
- `product_url`
- `price_text`
- `availability_text`
- `rating_text`
- `description`
- `source_page`
- `fetched_at`

The price will later be normalized from text such as `GBP 51.77` into a numeric `price_gbp` value.

### Robots Check

I requested:

`https://books.toscrape.com/robots.txt`

The response was **404 Not Found**, so **no robots file was found**.

A missing robots file is not treated as permission to scrape other websites. This assignment specifically uses Books to Scrape because it is a public practice sandbox intended for scraping practice.

### Why This Target Is Appropriate

Books to Scrape is explicitly provided as the practice sandbox for this assignment. The scraper will stay within the required first three catalogue pages and will use polite fetching practices such as an identifying user-agent, request timeout, caching, and a delay between real requests.

**I will not reuse this code on another site without checking its rules and terms first.**

## Status

Stage 0 - Target classification