import time
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from core.csv_io import write_products_csv
from core.http import build_headers
from core.models import ScrapeTarget
from core.settings import app_config
from core.utils import dedupe_products


class BaseScraper(ABC):
    store_name = ''
    display_name = ''
    base_url = ''
    output_file = ''
    extra_headers = None
    accept_language = None
    timeout = None
    delay = None
    max_pages = None
    max_categories = None
    default_output_dir = Path('data/items')

    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir or self.default_output_dir)
        self.timeout = app_config.get_scraper_timeout(self.store_name, self.timeout)
        self.delay = app_config.get_scraper_delay(self.store_name, self.delay)
        self.max_pages = app_config.get_scraper_max_pages(self.store_name, self.max_pages)
        self.max_categories = app_config.get_scraper_max_categories(self.store_name, self.max_categories)
        self.headers = build_headers(
            accept_language=app_config.get_scraper_accept_language(self.store_name, self.accept_language),
            extra_headers=self.extra_headers,
        )
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def log(self, message):
        print(message)

    def fetch_response(self, url):
        try:
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response
        except Exception as exc:
            self.log(f'Error reading {url}: {exc}')
            return None

    def parse_response(self, response):
        return BeautifulSoup(response.text, 'html.parser')

    def fetch_page(self, url):
        response = self.fetch_response(url)

        if response is None:
            return None

        return self.parse_response(response)

    def get_first_page_url(self, target_url):
        return target_url

    def get_output_path(self):
        return self.output_dir / self.output_file

    def iterate_target(self, target: ScrapeTarget):
        current_url = self.get_first_page_url(target.url)
        seen_product_names = set()
        page_num = 1

        while current_url and page_num <= self.max_pages:
            self.log(f'  - Scraping: {current_url}')
            page_data = self.fetch_page(current_url)

            if page_data is None:
                break

            products = self.extract_products_from_page(page_data, current_url)

            if not products:
                self.log('  - No more products in this target, ending target scrape.')
                break

            current_page_names = {product.name for product in products}

            if current_page_names and current_page_names.issubset(seen_product_names):
                self.log('  - Repeated product page detected, ending target scrape.')
                break

            for product in products:
                yield product

            seen_product_names.update(current_page_names)

            if not target.paginate:
                break

            next_url = self.get_next_page_url(current_url, page_num, page_data)

            if not next_url:
                break

            current_url = next_url
            page_num += 1
            time.sleep(self.delay)

    def run(self):
        self.log(f'Starting to scrape {self.display_name} product data...')
        all_products = []
        targets = self.get_target_urls()

        for index, target in enumerate(targets, start=1):
            if len(targets) == 1:
                self.log(f'Scraping {target.label}: {target.url}')
            else:
                self.log(f'\nScraping {target.label} ({index}/{len(targets)}): {target.url}')

            all_products.extend(self.iterate_target(target))

        unique_products = dedupe_products(all_products)
        output_path = self.get_output_path()
        write_products_csv(output_path, unique_products)
        self.log(
            f'\nScraping complete! Fetched {len(unique_products)} unique products, '
            f'saved to {output_path}'
        )
        return unique_products

    @abstractmethod
    def get_target_urls(self):
        raise NotImplementedError

    @abstractmethod
    def extract_products_from_page(self, page_data, url):
        raise NotImplementedError

    @abstractmethod
    def get_next_page_url(self, current_url, page_number, page_data):
        raise NotImplementedError
