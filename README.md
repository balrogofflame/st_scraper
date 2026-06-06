# ST Scraper

ST(Sex Toys) Scraper collects product pricing data from multiple adult-toy stores, saves each store's catalog to CSV, calculates pricing statistics, and generates SVG pricing visualizations from those results.

## What This Project Does

- Scrapes product names and prices from multiple stores under [scrapers](C:/Users/user/source/st_scraper/scrapers)
- Saves store-level product data to [data/items](C:/Users/user/source/st_scraper/data/items)
- Calculates pricing summaries such as mean, median, and standard deviation into [data/reports/st_stats.csv](C:/Users/user/source/st_scraper/data/reports/st_stats.csv)
- Builds pricing charts, including the gender-schema pricing chart, from the stats report

## Project Structure

- [main.py](C:/Users/user/source/st_scraper/main.py): main entry point
- [scrapers](C:/Users/user/source/st_scraper/scrapers): store-specific scraper modules
- [core](C:/Users/user/source/st_scraper/core): shared scraping infrastructure
- [stats](C:/Users/user/source/st_scraper/stats): stats calculation and plotting logic
- [data/items](C:/Users/user/source/st_scraper/data/items): scraped CSV outputs
- [data/reports](C:/Users/user/source/st_scraper/data/reports): generated reports and charts
- [assets/store_logos](C:/Users/user/source/st_scraper/assets/store_logos): store logo assets
- [config/exchangerate_api.txt](C:/Users/user/source/st_scraper/config/exchangerate_api.txt): exchange-rate API key
- [config/gender_schema.csv](C:/Users/user/source/st_scraper/config/gender_schema.csv): store gender-schema scores

## Getting Started

### 1. Create or activate a virtual environment

If you already have the project venv:

```powershell
.\.venv\Scripts\Activate.ps1
```

If you need to create one:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Add your exchange-rate API key

Put your key in:

```text
config/exchangerate_api.txt
```

This is used when converting non-TWD prices during stats generation.

## Common Commands

Scrape all stores:

```powershell
python main.py scrape all
```

Scrape specific stores:

```powershell
python main.py scrape drqq tenga womanizer
```

Generate the stats report:

```powershell
python main.py stats
```

Generate the pricing SVG chart:

```powershell
python main.py plot-pricing
```

Run tests:

```powershell
python -m unittest discover -s tests -v
```

## Output Files

- Store CSVs: [data/items](C:/Users/user/source/st_scraper/data/items)
- Stats report: [data/reports/st_stats.csv](C:/Users/user/source/st_scraper/data/reports/st_stats.csv)
- Pricing chart: [data/reports/store_pricing_min.svg](C:/Users/user/source/st_scraper/data/reports/store_pricing_min.svg)

## Contributor

Chang Chen-Hsun is the main contributor to this project.
