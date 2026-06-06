from core.http import build_headers
from core.models import ScrapeTarget
from core.registry import register_scraper
from core.utils import build_url_with_query
from scrapers.families.shopline_html import ShoplineHtmlScraper


@register_scraper('iroha')
class IrohaScraper(ShoplineHtmlScraper):
    store_name = 'iroha'
    display_name = 'iroha'
    base_url = 'https://www.iroha.tw/'
    products_url = f'{base_url}products'
    output_file = 'iroha.csv'
    headers = build_headers('zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7')
    max_pages = 100
    timeout = 10
    delay = 1
    item_selector = '.product-item a.Product-item'

    def get_target_urls(self):
        return [ScrapeTarget(url=self.products_url, label='product listing', paginate=True)]

    def get_first_page_url(self, target_url):
        return build_url_with_query(target_url, {'limit': 24})

    def build_page_url(self, current_url, page_num):
        if page_num == 1:
            return self.get_first_page_url(current_url)

        return build_url_with_query(current_url, {
            'page': page_num,
            'sort_by': '',
            'order_by': '',
            'limit': 24
        })
