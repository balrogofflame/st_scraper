# ST Scraper

ST(Sex Toys) Scraper collects product pricing data from multiple adult-toy stores, saves each store's catalog to CSV, calculates pricing statistics, and generates SVG pricing visualizations from those results.

## What This Project Does

- Scrapes product names and prices from multiple stores under [scrapers](scrapers)
- Saves store-level product data to [data/items](data/items)
- Calculates pricing summaries such as mean, median, and standard deviation into [data/reports/st_stats.csv](data/reports/st_stats.csv)
- Builds pricing charts, including the gender-imagery pricing chart, from the stats report

## Project Structure

- [main.py](main.py): main entry point
- [scrapers](scrapers): store-specific scraper modules
- [core](core): shared scraping infrastructure
- [stats](stats): stats calculation and plotting logic
- [data/items](data/items): scraped CSV outputs
- [data/reports](data/reports): generated reports and charts
- [assets/store_logos](assets/store_logos): store logo assets
- [config/exchangerate_api.txt](config/exchangerate_api.txt): exchange-rate API key
- [config/gender_imagery_score.csv](config/gender_imagery_score.csv): store gender imagery scores

## Getting Started

### 1. Create the Conda environment

```powershell
conda env create -f environment.yml
conda activate st-scraper
```

### 2. Create your local scraper config

```powershell
Copy-Item .env.example .env
```

You can leave `.env` absent if the built-in defaults are fine.

### 3. Add your exchange-rate API key

Put your key in:

```text
config/exchangerate_api.txt
```

This is used when converting non-TWD prices during stats generation.

## System Specifications

Recommended environment:

- Operating system: Windows 10 or Windows 11
- Shell: PowerShell
- Python: 3.12
- Environment and dependency manager: Conda

Project/runtime requirements:

- Internet access is needed for live scraping and for refreshing exchange-rate data
- Optional local overrides can be stored in `.env`
- [assets/store_logos](assets/store_logos) must be present for logo-based charts
- A valid key in [config/exchangerate_api.txt](config/exchangerate_api.txt) is recommended when exchange-rate cache files are stale or missing
- Enough free disk space for CSV outputs, generated SVG/PNG charts, and the virtual environment

## Required Files Check

Before running commands, make sure these files and folders exist:

- [main.py](main.py)
- [config/gender_imagery_score.csv](config/gender_imagery_score.csv)
- [assets/store_logos](assets/store_logos)
- [data/items](data/items) if you want to run `stats` on existing scraped data
- [data/reports/st_stats.csv](data/reports/st_stats.csv) if you want to run `plot-pricing` on an existing stats report

Also check [config/exchangerate_api.txt](config/exchangerate_api.txt):

- If it exists and contains a valid key, exchange rates can be refreshed
- If it is missing, the project can still work only when a usable cached exchange-rate file already exists in [data/cache/exchange_rates](data/cache/exchange_rates)

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

- Store CSVs: [data/items](data/items)
- Stats report: [data/reports/st_stats.csv](data/reports/st_stats.csv)
- Pricing chart: [data/reports/store_pricing_min.svg](data/reports/store_pricing_min.svg)

## Important Run Order (for non-technical users)

Conda is used to create and manage the project's Python environment. It ensures the correct Python version and dependencies are installed and isolated from your system Python, which prevents conflicts and makes the project reproducible. Download and install Anaconda (or Miniconda) from the [Anaconda official download page](https://www.anaconda.com/download) before proceeding.

The order of running `main.py` matters.

If you are new to working with a repository, do not treat the commands as interchangeable. A later step depends on files created by an earlier step.

Recommended order:

1. `conda activate st-scraper`
2. `python main.py scrape ...`
3. `python main.py stats`
4. `python main.py plot-pricing`

Why this matters:

- `scrape` creates or updates the store CSV files in [data/items](data/items)
- `stats` reads those CSV files and creates [data/reports/st_stats.csv](data/reports/st_stats.csv)
- `plot-pricing` reads [data/reports/st_stats.csv](data/reports/st_stats.csv) and the logo files to create the SVG chart

Possible consequences if you run commands in the wrong order:

- Running `python main.py plot-pricing` before a valid [data/reports/st_stats.csv](data/reports/st_stats.csv) exists can raise `ValueError('No pricing points found.')`
- Running `python main.py plot-pricing` when the stats file path is missing can raise `FileNotFoundError`
- Running `python main.py stats` before the store CSV files exist can produce `No CSV files selected.`
- Running `python main.py stats missing.csv` can raise `FileNotFoundError`
- Running `python main.py stats` when exchange-rate data is needed but both the API key and cache are unavailable can fail during currency conversion

In short:

- Do not run `plot-pricing` before `stats` unless [data/reports/st_stats.csv](data/reports/st_stats.csv) already exists and contains valid data
- Do not run `stats` before `scrape` unless [data/items](data/items) already contains the CSV files you want to analyze

## Contributor

Chang Chen-Hsun is the main contributor to this project.
