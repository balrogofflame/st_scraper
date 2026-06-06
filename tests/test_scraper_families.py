import unittest

from bs4 import BeautifulSoup

from core.models import Product, ScrapeTarget
from scrapers.families.shopline_html import ShoplineHtmlScraper
from scrapers.families.simple_paged_html import SimplePagedHtmlScraper


class DummyShoplineScraper(ShoplineHtmlScraper):
    store_name = 'dummy-shopline'
    display_name = 'Dummy Shopline'
    base_url = 'https://example.com/'
    output_file = 'dummy.csv'

    def get_target_urls(self):
        return [ScrapeTarget(url=self.base_url, paginate=False)]


class DummySimpleScraper(SimplePagedHtmlScraper):
    store_name = 'dummy-simple'
    display_name = 'Dummy Simple'
    base_url = 'https://example.com/'
    output_file = 'dummy.csv'

    def get_target_urls(self):
        return [ScrapeTarget(url=self.base_url, paginate=False)]


class ScraperFamiliesTestCase(unittest.TestCase):
    def test_shopline_html_extracts_name_and_price(self):
        scraper = DummyShoplineScraper()
        soup = BeautifulSoup(
            '<a class="quick-cart-item" href="/p1">'
            '<span class="title"> Demo Item </span>'
            '<span class="quick-cart-price"> NT$1,000 </span>'
            '</a>',
            'html.parser'
        )

        self.assertEqual(
            scraper.extract_products_from_page(soup, 'https://example.com'),
            [Product(name='Demo Item', price='NT$1,000')]
        )

    def test_simple_paged_html_extracts_regex_prices(self):
        scraper = DummySimpleScraper()
        soup = BeautifulSoup(
            '<a href="/products/a" class="group block cursor-pointer">'
            '<h3>Demo Item</h3>'
            '<span>NT$990</span>'
            '</a>',
            'html.parser'
        )

        self.assertEqual(
            scraper.extract_products_from_page(soup, 'https://example.com'),
            [Product(name='Demo Item', price='NT$990')]
        )


if __name__ == '__main__':
    unittest.main()
