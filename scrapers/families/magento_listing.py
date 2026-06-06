from core.base_scraper import BaseScraper
from core.models import Product
from core.utils import clean_text


class MagentoListingScraper(BaseScraper):
    def get_next_page_url(self, current_url, page_number, page_data):
        return None

    def extract_products_from_page(self, page_data, url):
        products = []

        for item in page_data.select('.product__info.product-item-info'):
            name = self.get_product_name(item)
            price = self.get_product_price(item)

            if name and price:
                products.append(Product(name=name, price=price))

        return products

    def get_product_name(self, item):
        name_tag = item.select_one('.product__name')

        if name_tag:
            name = clean_text(name_tag.get_text())

            if name:
                return name

        data_name_tag = item.select_one('[data-name]')

        if data_name_tag:
            name = clean_text(data_name_tag.get('data-name', ''))

            if name:
                if name.lower().startswith('womanizer'):
                    return name

                return f'Womanizer {name}'

        img_tag = item.find('img', alt=True)

        if img_tag:
            return clean_text(img_tag.get('alt', ''))

        return ''

    def get_product_price(self, item):
        prices = []

        for tag in item.select('.special-price .price, .old-price .price, .normal-price .price, .price'):
            price = clean_text(tag.get_text())

            if price and price not in prices:
                prices.append(price)

        if prices:
            return ' '.join(prices)

        price_box = item.select_one('.price-box')

        if price_box:
            return clean_text(price_box.get_text(' '))

        return ''
