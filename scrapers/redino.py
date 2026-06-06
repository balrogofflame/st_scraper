from core.http import build_headers
from core.models import ScrapeTarget
from core.registry import register_scraper
from core.utils import build_url_with_query
from scrapers.families.shopline_html import ShoplineHtmlScraper


@register_scraper('redino')
class RedinoScraper(ShoplineHtmlScraper):
    store_name = 'redino'
    display_name = 'Redino'
    base_url = 'https://www.redino.tw/'
    products_url = f'{base_url}categories/newbie'
    output_file = 'redino.csv'
    headers = build_headers('zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7')
    max_pages = 100
    timeout = 10
    delay = 1

    def get_target_urls(self):
        return [ScrapeTarget(url=self.products_url, label='product listing', paginate=True)]

    def get_first_page_url(self, target_url):
        return self.build_page_url(target_url, 1)

    def build_page_url(self, current_url, page_num):
        return build_url_with_query(current_url, {
            'page': page_num,
            'sort_by': '',
            'order_by': '',
            'limit': 72
        })
