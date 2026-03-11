# UVU Africa Innovation Ecosystem Dashboard

A data analytics project that tells the story of UVU Africa's impact on Africa's digital economy — using public data, automated pipelines, and interactive dashboards.

---

## Project Overview

This project was built to analyse and visualise the innovation ecosystem around **UVU Africa** (formerly CiTi), one of Africa's leading technology and entrepreneurship organisations based in Cape Town.

The dashboard answers key business questions such as:

- How many startups has UVU Africa supported, and in which sectors?
- What is the talent pipeline impact of programmes like CAPACITI?
- Which technology sectors are growing fastest in the African ecosystem?
- How has UVU Africa's geographic reach expanded over time?
- Who are the key ecosystem partners and collaborators?

---

## Project Structure

```
uvu_africa_analytics/
│
├── data/                        # All datasets (CSV)
│   ├── programs.csv             # UVU Africa programmes
│   ├── startups.csv             # Startups supported
│   ├── talent_programs.csv      # Graduate & placement data
│   ├── partners.csv             # Ecosystem partners
│   └── news_mentions.csv        # Media & ecosystem mentions
│
├── pipelines/                   # Data collection scripts
│   ├── scrape_uvu_news.py       # Scrapes news mentions
│   ├── generate_startups.py     # Generates startup ecosystem data
│   └── update_pipeline.py       # Master pipeline runner + cleaner
│
├── dashboard/                   # Streamlit dashboard
│   └── app.py                   # Main dashboard application
│
├── notebooks/                   # Exploratory analysis (Jupyter)
│
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## Datasets

| File | Rows | Description |
|---|---|---|
| `programs.csv` | 10 | UVU Africa programmes (CAPACITI, Injini, UVU Bio, etc.) |
| `startups.csv` | 106 | Startups by sector, country, funding, and status |
| `talent_programs.csv` | 21 | Graduate counts, placement rates, and top skills per year |
| `partners.csv` | 20 | Corporate, university, and government partners |
| `news_mentions.csv` | 100 | Media articles with dates, sources, and topics |

### Table Relationships

```
programs
   │
   └── startups  (programs.program_id = startups.program_id)

talent_programs   → workforce impact analysis
partners          → ecosystem network analysis
news_mentions     → innovation theme analysis
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/ZolileN/uvu_africa_analytics.git
cd uvu_africa_analytics
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Data Pipeline

Generate and refresh all datasets:

```bash
python pipelines/generate_startups.py
python pipelines/scrape_uvu_news.py
```

Or run the master pipeline:

```bash
python pipelines/update_pipeline.py
```

### 4. Launch the Dashboard

```bash
streamlit run dashboard/app.py
```

Your browser will open at `http://localhost:8501` with the live dashboard.

---

## Dashboard Pages

| Page | Description |
|---|---|
| **Executive Overview** | KPIs: total startups, programmes, partners, graduates |
| **Startup Ecosystem** | Funding by sector, country distribution, growth trends |
| **Talent Pipeline** | Graduates per year, placement rates, in-demand skills |
| **Ecosystem Partners** | Partner network by type, sector, and geography |
| **Innovation Trends** | Media mentions, topic frequency, sentiment analysis |

---

## Automated Pipeline

The pipeline can be scheduled to run automatically every morning using `cron` (Linux/macOS):

```bash
crontab -e
```

Add the following line:

```
0 7 * * * python3 /path/to/uvu_africa_analytics/pipelines/update_pipeline.py
```

This will:
1. Scrape new ecosystem news
2. Clean and deduplicate datasets
3. Refresh the dashboard data automatically

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| pandas | Data cleaning & transformation |
| requests + BeautifulSoup | Web scraping |
| Streamlit | Interactive dashboard |
| Plotly | Data visualisation |
| scikit-learn | Predictive insights (bonus feature) |
| cron | Pipeline scheduling |

---

## Key Insights (Sample)

- **Talent programmes** have shown consistent growth in graduate placement rates, exceeding 70% in most years.
- **FinTech, EdTech, and AI/ML** are the dominant startup sectors supported across UVU Africa programmes.
- **Cape Town** remains the core innovation hub, with emerging ecosystems in Johannesburg, Durban, and Kigali.
- **Corporate technology partners** (Microsoft, AWS, Google) make up the largest segment of the ecosystem network.
- **Digital skills and AI** have become the most frequently discussed innovation themes since 2022.

---

## Author

Built by Zolile Nonzapa as a portfolio analytics project for a Data Analyst role application at **UVU Africa**.

---

## License

This project is for educational and portfolio purposes only. All data used is either publicly available or synthetically generated for demonstration.