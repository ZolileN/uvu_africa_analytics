"""
update_pipeline.py
──────────────────
Master pipeline runner for the UVU Africa Ecosystem Dashboard.

This script orchestrates the full data refresh cycle:
  1. Regenerate / update startup ecosystem data
  2. Scrape latest news mentions
  3. Clean and deduplicate all datasets
  4. Log a run summary with row counts and data quality stats

Schedule this script to run daily using cron:
  0 7 * * * python3 /path/to/uvu_africa_analytics/pipelines/update_pipeline.py

Usage:
    python pipelines/update_pipeline.py
    python pipelines/update_pipeline.py --clean-only
    python pipelines/update_pipeline.py --scrape-only
"""

import os
import sys
import logging
import argparse
import pandas as pd
from datetime import datetime

# Allow imports from sibling pipeline scripts
sys.path.insert(0, os.path.dirname(__file__))

# ── Logging ───────────────────────────────────────────────────────────────────

LOG_DIR  = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, f"pipeline_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file),
    ],
)
log = logging.getLogger(__name__)

# ── Data Paths ────────────────────────────────────────────────────────────────

BASE_DIR  = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR  = os.path.join(BASE_DIR, "data")

DATASETS = {
    "programs":       os.path.join(DATA_DIR, "programs.csv"),
    "startups":       os.path.join(DATA_DIR, "startups.csv"),
    "talent":         os.path.join(DATA_DIR, "talent_programs.csv"),
    "partners":       os.path.join(DATA_DIR, "partners.csv"),
    "news_mentions":  os.path.join(DATA_DIR, "news_mentions.csv"),
}

# ── Step 1 — Run Scrapers ─────────────────────────────────────────────────────

def run_scrapers():
    """Run all data collection scripts."""
    log.info("━━━━ STEP 1: Running data scrapers ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    try:
        from generate_startups import main as gen_startups
        log.info("Running generate_startups ...")
        gen_startups()
    except Exception as e:
        log.error(f"generate_startups failed: {e}")

    try:
        from scrape_uvu_news import main as scrape_news
        log.info("Running scrape_uvu_news ...")
        scrape_news()
    except Exception as e:
        log.error(f"scrape_uvu_news failed: {e}")


# ── Step 2 — Clean All Datasets ───────────────────────────────────────────────

def clean_dataset(name: str, path: str) -> pd.DataFrame | None:
    """Load, clean, and return a single dataset."""
    if not os.path.exists(path):
        log.warning(f"  [{name}] File not found: {path}")
        return None

    df = pd.read_csv(path)
    original_rows = len(df)

    # Remove fully empty rows
    df.dropna(how="all", inplace=True)

    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())

    # Dataset-specific cleaning
    if name == "startups":
        df["funding_usd"] = pd.to_numeric(df["funding_usd"], errors="coerce").fillna(0).astype(int)
        df["founded_year"] = pd.to_numeric(df["founded_year"], errors="coerce")
        df.drop_duplicates(subset=["startup_name", "country"], inplace=True)

    elif name == "news_mentions":
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["year"] = df["date"].dt.year
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        df.drop_duplicates(subset=["title", "source"], inplace=True)
        df.sort_values("date", ascending=False, inplace=True)
        # Re-index article IDs
        df.reset_index(drop=True, inplace=True)
        df["article_id"] = df.index + 1

    elif name == "talent":
        df["placement_rate"] = (
            df["job_placements"] / df["graduates"]
        ).round(2)

    elif name == "programs":
        df["start_year"] = pd.to_numeric(df["start_year"], errors="coerce")

    removed = original_rows - len(df)
    log.info(f"  [{name}] {original_rows} → {len(df)} rows ({removed} removed)")

    return df


def run_cleaning():
    """Clean all datasets and save back to CSV."""
    log.info("━━━━ STEP 2: Cleaning datasets ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for name, path in DATASETS.items():
        df = clean_dataset(name, path)
        if df is not None:
            df.to_csv(path, index=False)


# ── Step 3 — Data Quality Report ─────────────────────────────────────────────

def run_quality_report():
    """Print a summary of each dataset after cleaning."""
    log.info("━━━━ STEP 3: Data quality report ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    report_rows = []

    for name, path in DATASETS.items():
        if not os.path.exists(path):
            log.warning(f"  [{name}] Missing — skipped")
            continue

        df = pd.read_csv(path)
        null_pct = round(df.isnull().mean().mean() * 100, 1)

        report_rows.append({
            "dataset":   name,
            "rows":      len(df),
            "columns":   len(df.columns),
            "nulls_%":   null_pct,
        })

        log.info(
            f"  {name:<20} rows={len(df):<6} cols={len(df.columns):<4} nulls={null_pct}%"
        )

    # Save report as CSV for dashboard display
    report_path = os.path.join(DATA_DIR, "pipeline_report.csv")
    report_df = pd.DataFrame(report_rows)
    report_df["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_df.to_csv(report_path, index=False)
    log.info(f"\n  Quality report saved to: {report_path}")


# ── Step 4 — Ecosystem Summary Stats ─────────────────────────────────────────

def run_summary():
    """Print high-level ecosystem stats from all datasets."""
    log.info("━━━━ STEP 4: Ecosystem summary ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    try:
        startups  = pd.read_csv(DATASETS["startups"])
        talent    = pd.read_csv(DATASETS["talent"])
        partners  = pd.read_csv(DATASETS["partners"])
        news      = pd.read_csv(DATASETS["news_mentions"])

        total_funding   = startups["funding_usd"].sum()
        active_startups = (startups["status"] == "Active").sum()
        total_grads     = talent["graduates"].sum()
        total_placed    = talent["job_placements"].sum()
        avg_placement   = round(total_placed / total_grads * 100, 1) if total_grads > 0 else 0

        log.info(f"  Startups in ecosystem:   {len(startups)}")
        log.info(f"  Active startups:         {active_startups}")
        log.info(f"  Total funding tracked:   ${total_funding:,.0f}")
        log.info(f"  Ecosystem partners:      {len(partners)}")
        log.info(f"  Graduates trained:       {total_grads:,}")
        log.info(f"  Jobs placed:             {total_placed:,}")
        log.info(f"  Avg placement rate:      {avg_placement}%")
        log.info(f"  News articles tracked:   {len(news)}")

    except Exception as e:
        log.error(f"Summary failed: {e}")


# ── CLI Argument Parser ───────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="UVU Africa Data Pipeline Runner")
    parser.add_argument(
        "--clean-only",
        action="store_true",
        help="Only run the cleaning step, skip scraping",
    )
    parser.add_argument(
        "--scrape-only",
        action="store_true",
        help="Only run the scraping step, skip cleaning",
    )
    return parser.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    log.info("══════════════════════════════════════════════════════════════════")
    log.info("  UVU Africa Ecosystem Dashboard — Data Pipeline")
    log.info(f"  Run started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("══════════════════════════════════════════════════════════════════")

    if args.clean_only:
        run_cleaning()
        run_quality_report()
    elif args.scrape_only:
        run_scrapers()
    else:
        run_scrapers()
        run_cleaning()
        run_quality_report()
        run_summary()

    log.info("══════════════════════════════════════════════════════════════════")
    log.info(f"  Pipeline complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"  Log saved to: {log_file}")
    log.info("══════════════════════════════════════════════════════════════════")


if __name__ == "__main__":
    main()