from urllib.parse import urlparse

from core.models import ScrapeTarget
from core.registry import register_scraper
from scrapers.families.shopline_html import ShoplineHtmlScraper


@register_scraper('drqq')
class DrqqScraper(ShoplineHtmlScraper):
    store_name = 'drqq'
    display_name = 'DRQQ'
    base_url = 'https://www.drqq.toys/'
    output_file = 'drqq.csv'
    static_targets = (
        ScrapeTarget(url=base_url, label='homepage', paginate=False),
    )
    category_source_urls = (base_url,)

    def should_include_category_url(self, href, full_url):
        parsed = urlparse(full_url)

        return (
            parsed.netloc == urlparse(self.base_url).netloc
            and '/categories/' in href
            and 'page=' not in href
        )
