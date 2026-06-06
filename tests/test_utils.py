import unittest

from core.models import Product
from core.utils import build_url_with_query, clean_text, dedupe_products, format_currency_amount, normalize_url


class UtilsTestCase(unittest.TestCase):
    def test_clean_text_collapses_whitespace(self):
        self.assertEqual(clean_text('  hello \n world  '), 'hello world')

    def test_normalize_url_removes_trailing_slash_and_query(self):
        normalized = normalize_url('https://example.com/', '/products/item/?page=2')
        self.assertEqual(normalized, 'https://example.com/products/item')

    def test_build_url_with_query_merges_values(self):
        updated = build_url_with_query('https://example.com/items?limit=24', {'page': 2})
        self.assertEqual(updated, 'https://example.com/items?limit=24&page=2')

    def test_dedupe_products_keeps_last_product_by_name(self):
        products = [
            Product(name='A', price='NT$100'),
            Product(name='A', price='NT$120'),
        ]
        unique_products = dedupe_products(products)
        self.assertEqual(unique_products, [Product(name='A', price='NT$120')])

    def test_format_currency_amount_supports_eur(self):
        self.assertEqual(format_currency_amount('199', 'EUR'), '€199')


if __name__ == '__main__':
    unittest.main()
