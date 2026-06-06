from core.http import build_headers
from core.models import ScrapeTarget
from core.registry import register_scraper
from scrapers.families.simple_paged_html import SimplePagedHtmlScraper


@register_scraper('ayce')
class AyceScraper(SimplePagedHtmlScraper):
    store_name = 'ayce'
    display_name = 'AYCE'
    base_url = 'https://www.ayce.com.tw/'
    products_url = f'{base_url}products'
    output_file = 'ayce.csv'
    headers = build_headers('zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7')
    max_pages = 100
    timeout = 10
    delay = 1
    item_selector = 'a.group.block.cursor-pointer[href^="/products/"]'

    def get_target_urls(self):
        return [ScrapeTarget(url=self.products_url, label='product listing', paginate=True)]
