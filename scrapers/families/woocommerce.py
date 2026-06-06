from core.base_scraper import BaseScraper
from core.models import Product
from core.utils import clean_text


class WooCommerceScraper(BaseScraper):
    def extract_products_from_page(self, page_data, url):
        products = []

        for item in page_data.find_all('li', class_='product'):
            name_tag = item.find('h2', class_='woocommerce-loop-product__title')
            price_tag = item.find('span', class_='price')

            if name_tag and price_tag:
                products.append(Product(
                    name=clean_text(name_tag.get_text()),
                    price=clean_text(price_tag.get_text(' '))
                ))

        return products

    def get_next_page_url(self, current_url, page_number, page_data):
        base_url = current_url.rstrip('/')

        if '/page/' in base_url:
            base_url = base_url.rsplit('/page/', 1)[0]

        return f'{base_url}/page/{page_number + 1}/'
