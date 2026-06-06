from core.http import build_headers
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
    headers = build_headers('zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7')
    max_pages = 100
    timeout = 10
    delay = 1

    def get_target_urls(self):
        return [ScrapeTarget(url=self.products_url, label='product listing', paginate=True)]
