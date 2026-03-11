"""
scrape_uvu_news.py
──────────────────
Scrapes news articles mentioning UVU Africa from:
  - TechCabal      (techcabal.com)
  - Disrupt Africa (disruptafrica.com)
  - Ventureburn    (ventureburn.com)

Results are appended to data/news_mentions.csv.
Duplicates are removed automatically after each run.

Usage:
    python pipelines/scrape_uvu_news.py
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import logging
from datetime import datetime

# ── Configuration ─────────────────────────────────────────────────────────────

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "news_mentions.csv")

SEARCH_URLS = [
    {
        "source": "TechCabal",
        "url": "https://techcabal.com/?s=uvu+africa",
        "article_tag": "article",
        "title_tag": "h2",
        "date_tag": "time",
    },
    {
        "source": "Disrupt Africa",
        "url": "https://disruptafrica.com/?s=uvu+africa",
        "article_tag": "article",
        "title_tag": "h2",
        "date_tag": "time",
    },
    {
        "source": "Ventureburn",
        "url": "https://ventureburn.com/?s=uvu+africa",
        "article_tag": "article",
        "title_tag": "h2",
        "date_tag": "time",
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ── Logging setup ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Scraper ───────────────────────────────────────────────────────────────────

def scrape_source(config: dict) -> list[dict]:
    """Scrape a single news source and return a list of article dicts."""
    articles = []
    source = config["source"]

    try:
        log.info(f"Scraping {source} ...")
        response = requests.get(config["url"], headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        posts = soup.find_all(config["article_tag"])

        if not posts:
            log.warning(f"No articles found on {source}. Page structure may have changed.")
            return articles

        for post in posts:
            title_el = post.find(config["title_tag"])
            date_el  = post.find(config["date_tag"])

            title = title_el.get_text(strip=True) if title_el else "Unknown Title"
            date  = date_el.get("datetime") or (date_el.get_text(strip=True) if date_el else None)

            # Attempt to parse date
            parsed_date = None
            if date:
                for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%B %d, %Y", "%d %B %Y"):
                    try:
                        parsed_date = datetime.strptime(date[:10], fmt[:len(date[:10])])
                        break
                    except ValueError:
                        continue

            articles.append({
                "title":     title,
                "source":    source,
                "date":      parsed_date.strftime("%Y-%m-%d") if parsed_date else date,
                "year":      parsed_date.year if parsed_date else None,
                "topic":     classify_topic(title),
                "sentiment": "Positive",  # default; extend with NLP if desired
            })

        log.info(f"  → {len(articles)} articles collected from {source}")

    except requests.exceptions.RequestException as e:
        log.error(f"Failed to reach {source}: {e}")

    return articles


def classify_topic(title: str) -> str:
    """Simple keyword-based topic classifier."""
    title_lower = title.lower()
    keyword_map = {
        "FinTech":        ["fintech", "payment", "banking", "finance", "financial"],
        "EdTech":         ["edtech", "education", "learning", "school", "university"],
        "AI/ML":          ["ai", "artificial intelligence", "machine learning", "data"],
        "Biotechnology":  ["biotech", "biology", "lab", "genomics", "health"],
        "Digital Skills": ["skills", "training", "graduates", "capaciti", "talent"],
        "CleanTech":      ["clean", "solar", "energy", "climate", "green"],
        "Startup Funding":["funding", "investment", "raise", "venture", "capital"],
        "Innovation Policy": ["government", "policy", "regulation", "initiative"],
    }
    for topic, keywords in keyword_map.items():
        if any(kw in title_lower for kw in keywords):
            return topic
    return "General"


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    all_articles = []

    for config in SEARCH_URLS:
        articles = scrape_source(config)
        all_articles.extend(articles)

    if not all_articles:
        log.warning("No new articles scraped. Exiting without updating CSV.")
        return

    new_df = pd.DataFrame(all_articles)

    # Load existing data if available
    if os.path.exists(DATA_PATH):
        existing_df = pd.read_csv(DATA_PATH)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df

    # Deduplicate on title + source
    before = len(combined_df)
    combined_df.drop_duplicates(subset=["title", "source"], inplace=True)
    after = len(combined_df)

    # Re-index article IDs
    combined_df.reset_index(drop=True, inplace=True)
    combined_df.insert(0, "article_id", combined_df.index + 1)

    # Save
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    combined_df.to_csv(DATA_PATH, index=False)

    log.info(f"news_mentions.csv updated: {after} rows ({before - after} duplicates removed)")
    log.info(f"Saved to: {os.path.abspath(DATA_PATH)}")


if __name__ == "__main__":
    main()