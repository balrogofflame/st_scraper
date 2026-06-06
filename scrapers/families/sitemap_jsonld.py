import gzip
import xml.etree.ElementTree as ET

from core.base_scraper import BaseScraper
from core.models import ScrapeTarget
from core.utils import extract_json_ld_product


class SitemapJsonLdScraper(BaseScraper):
    sitemap_url = ''
    sitemap_is_gzipped = False

    def get_target_urls(self):
        sitemap_bytes = self.fetch_sitemap_bytes()

        if sitemap_bytes is None:
            return []

        root = ET.fromstring(sitemap_bytes)
        product_urls = self.extract_product_urls_from_sitemap(root)

        return [ScrapeTarget(url=url, label='product page', paginate=False) for url in product_urls]

    def fetch_sitemap_bytes(self):
        response = self.fetch_response(self.sitemap_url)

        if response is None:
            return None

        data = response.content

        if self.sitemap_is_gzipped:
            return gzip.decompress(data)

        return data

    def extract_products_from_page(self, page_data, url):
        product = extract_json_ld_product(page_data)

        if product is None:
            return []

        return [product]

    def get_next_page_url(self, current_url, page_number, page_data):
        return None

    def iter_elements(self, root, tag_name):
        for element in root.iter():
            if element.tag.split('}')[-1] == tag_name:
                yield element

    def extract_product_urls_from_sitemap(self, root):
        raise NotImplementedError
