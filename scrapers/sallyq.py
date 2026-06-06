from urllib.parse import urljoin

from core.http import build_headers
from core.models import ScrapeTarget
from core.registry import register_scraper
from core.utils import normalize_url
from scrapers.families.woocommerce import WooCommerceScraper


@register_scraper('sallyq')
class SallyqScraper(WooCommerceScraper):
    store_name = 'sallyq'
    display_name = 'SallyQ'
    base_url = 'https://www.sallyq.com.tw/'
    output_file = 'sallyq.csv'
    headers = build_headers()
    timeout = 10
    delay = 1
    max_pages = 100

    def get_target_urls(self):
        targets = [ScrapeTarget(url=self.base_url, label='homepage', paginate=False)]
        category_urls = []
        seen_urls = set()
        soup = self.fetch_page(self.base_url)

        if soup is None:
            return targets

        for link in soup.find_all('a', href=True):
            href = link['href']

            if 'product-category' not in href or '/page/' in href:
                continue

            full_url = normalize_url(self.base_url, urljoin(self.base_url, href))

            if full_url in seen_urls:
                continue

            seen_urls.add(full_url)
            category_urls.append(full_url)

        for url in category_urls[:50]:
            targets.append(ScrapeTarget(url=url, label='category', paginate=True))

        return targets
