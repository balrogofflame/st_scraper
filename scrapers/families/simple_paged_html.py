import re

from core.base_scraper import BaseScraper
from core.models import Product
from core.utils import build_url_with_query, clean_text


class SimplePagedHtmlScraper(BaseScraper):
    item_selector = 'a[href^="/products/"]'
    product_name_selector = 'h3'
    price_pattern = re.compile(r'NT\$\s*[\d,]+')

    def extract_products_from_page(self, page_data, url):
        products = []

        for item in page_data.select(self.item_selector):
            name = self.get_product_name(item)
            price = self.get_product_price(item)

            if name and price:
                products.append(Product(name=name, price=price))

        return products

    def get_product_name(self, item):
        name_tag = item.select_one(self.product_name_selector)

        if name_tag:
            name = clean_text(name_tag.get_text())

            if name:
                return name

        img_tag = item.find('img', alt=True)

        if img_tag:
            return clean_text(img_tag.get('alt', ''))

        return ''

    def get_product_price(self, item):
        prices = []

        for match in self.price_pattern.findall(item.get_text(' ', strip=True)):
            price = clean_text(match)

            if price and price not in prices:
                prices.append(price)

        return ' '.join(prices)

    def get_next_page_url(self, current_url, page_number, page_data):
        return build_url_with_query(current_url, {'page': page_number + 1})
