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

## Required Files Check

Before running commands, make sure these files and folders exist:

- [main.py](C:/Users/user/source/st_scraper/main.py)
- [config/gender_schema.csv](C:/Users/user/source/st_scraper/config/gender_schema.csv)
- [assets/store_logos](C:/Users/user/source/st_scraper/assets/store_logos)
- [data/items](C:/Users/user/source/st_scraper/data/items) if you want to run `stats` on existing scraped data
- [data/reports/st_stats.csv](C:/Users/user/source/st_scraper/data/reports/st_stats.csv) if you want to run `plot-pricing` on an existing stats report

Also check [config/exchangerate_api.txt](C:/Users/user/source/st_scraper/config/exchangerate_api.txt):

- If it exists and contains a valid key, exchange rates can be refreshed
- If it is missing, the project can still work only when a usable cached exchange-rate file already exists in [data/cache/exchange_rates](C:/Users/user/source/st_scraper/data/cache/exchange_rates)

If one of these required files is missing, commands such as `stats` or `plot-pricing` may fail or produce incomplete output.

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

## Important Run Order (for non-technical users)

The order of running `main.py` matters.

If you are new to working with a repository, do not treat the commands as interchangeable. A later step depends on files created by an earlier step.

Recommended order:

1. `python main.py scrape ...`
2. `python main.py stats`
3. `python main.py plot-pricing`

Why this matters:

- `scrape` creates or updates the store CSV files in [data/items](C:/Users/user/source/st_scraper/data/items)
- `stats` reads those CSV files and creates [data/reports/st_stats.csv](C:/Users/user/source/st_scraper/data/reports/st_stats.csv)
- `plot-pricing` reads [data/reports/st_stats.csv](C:/Users/user/source/st_scraper/data/reports/st_stats.csv) and the logo files to create the SVG chart

Possible consequences if you run commands in the wrong order:

- Running `python main.py plot-pricing` before a valid [data/reports/st_stats.csv](C:/Users/user/source/st_scraper/data/reports/st_stats.csv) exists can raise `ValueError('No pricing points found.')`
- Running `python main.py plot-pricing` when the stats file path is missing can raise `FileNotFoundError`
- Running `python main.py stats` before the store CSV files exist can produce `No CSV files selected.`
- Running `python main.py stats missing.csv` can raise `FileNotFoundError`
- Running `python main.py stats` when exchange-rate data is needed but both the API key and cache are unavailable can fail during currency conversion

In short:

- Do not run `plot-pricing` before `stats` unless [data/reports/st_stats.csv](C:/Users/user/source/st_scraper/data/reports/st_stats.csv) already exists and contains valid data
- Do not run `stats` before `scrape` unless [data/items](C:/Users/user/source/st_scraper/data/items) already contains the CSV files you want to analyze

## Contributor

Chang Chen-Hsun is the main contributor to this project.
