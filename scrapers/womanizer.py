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

    def get_target_urls(self):
        return [ScrapeTarget(url=self.products_url, label='product listing', paginate=False)]
