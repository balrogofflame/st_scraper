from urllib.parse import urlparse

from core.http import build_headers
from core.models import ScrapeTarget
from core.registry import register_scraper
from scrapers.families.shopline_html import ShoplineHtmlScraper


@register_scraper('drqq')
class DrqqScraper(ShoplineHtmlScraper):
    store_name = 'drqq'
    display_name = 'DRQQ'
    base_url = 'https://www.drqq.toys/'
    output_file = 'drqq.csv'
    headers = build_headers('zh-TW,zh-Hant;q=0.9,en-US;q=0.8,en;q=0.7')
    max_pages = 100
    timeout = 10
    delay = 1
    static_targets = (
        ScrapeTarget(url=base_url, label='homepage', paginate=False),
    )
    category_source_urls = (base_url,)
    max_categories = 300

    def should_include_category_url(self, href, full_url):
        parsed = urlparse(full_url)

        return (
            parsed.netloc == urlparse(self.base_url).netloc
            and '/categories/' in href
            and 'page=' not in href
        )
