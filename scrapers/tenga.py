from urllib.parse import urlparse

from core.models import ScrapeTarget
from core.registry import register_scraper
from core.utils import build_url_with_query
from scrapers.families.shopline_html import ShoplineHtmlScraper


@register_scraper('tenga')
class TengaScraper(ShoplineHtmlScraper):
    store_name = 'tenga'
    display_name = 'TENGA'
    base_url = 'https://www.tenga.tw/'
    products_url = f'{base_url}products'
    output_file = 'tenga.csv'
    item_selector = '.product-item a.Product-item'
    static_targets = (
        ScrapeTarget(url=products_url, label='product listing', paginate=True),
    )
    category_source_urls = (base_url, products_url)

    def should_include_category_url(self, href, full_url):
        parsed = urlparse(full_url)

        return (
            parsed.netloc == urlparse(self.base_url).netloc
            and parsed.path.startswith('/categories/')
            and not parsed.path.startswith('/en/categories/')
            and 'page=' not in href
        )

    def build_page_url(self, current_url, page_num):
        if page_num == 1:
            return current_url

        return build_url_with_query(current_url, {
            'page': page_num,
            'sort_by': '',
            'order_by': '',
            'limit': 24
        })
