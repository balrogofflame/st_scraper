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
    item_selector = 'a.group.block.cursor-pointer[href^="/products/"]'

    def get_target_urls(self):
        return [ScrapeTarget(url=self.products_url, label='product listing', paginate=True)]
