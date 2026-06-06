from core.http import build_headers
from core.models import ScrapeTarget
from core.registry import register_scraper
from scrapers.families.magento_listing import MagentoListingScraper


@register_scraper('womanizer')
class WomanizerScraper(MagentoListingScraper):
    store_name = 'womanizer'
    display_name = 'Womanizer'
    base_url = 'https://www.womanizer.com/eu/'
    products_url = f'{base_url}all-products'
    output_file = 'womanizer.csv'
    headers = build_headers('en-US,en;q=0.9')
    timeout = 10
    delay = 1

    def get_target_urls(self):
        return [ScrapeTarget(url=self.products_url, label='product listing', paginate=False)]
