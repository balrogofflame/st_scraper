from core.models import ScrapeTarget
from core.registry import register_scraper
from scrapers.families.shopline_html import ShoplineHtmlScraper


@register_scraper('puresexy')
class PureSexyScraper(ShoplineHtmlScraper):
    store_name = 'puresexy'
    display_name = 'Pure Sexy'
    base_url = 'https://www.pure-sexy.com/'
    products_url = f'{base_url}categories/pure-sexy-collection'
    output_file = 'puresexy.csv'

    def get_target_urls(self):
        return [ScrapeTarget(url=self.products_url, label='product listing', paginate=True)]
