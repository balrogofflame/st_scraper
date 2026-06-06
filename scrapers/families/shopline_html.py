import json
from urllib.parse import urlparse

from core.base_scraper import BaseScraper
from core.models import Product, ScrapeTarget
from core.utils import build_url_with_query, clean_text, normalize_url


class ShoplineHtmlScraper(BaseScraper):
    item_selector = 'a.quick-cart-item, a.js-quick-cart-item'
    static_targets = ()
    category_source_urls = ()
    max_categories = None

    def get_target_urls(self):
        targets = list(self.static_targets)
        targets.extend(self.discover_category_targets())
        return targets

    def discover_category_targets(self):
        category_urls = []
        seen_urls = set()

        for source_url in self.category_source_urls:
            soup = self.fetch_page(source_url)

            if soup is None:
                continue

            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = normalize_url(self.base_url, href)

                if full_url in seen_urls:
                    continue

                if not self.should_include_category_url(href, full_url):
                    continue

                seen_urls.add(full_url)
                category_urls.append(full_url)

        if self.max_categories is not None:
            category_urls = category_urls[:self.max_categories]

        return [ScrapeTarget(url=url, label='category', paginate=True) for url in category_urls]

    def should_include_category_url(self, href, full_url):
        parsed = urlparse(full_url)
        base_host = urlparse(self.base_url).netloc

        return (
            parsed.netloc == base_host
            and '/categories/' in href
            and 'page=' not in href
        )

    def get_product_name(self, item):
        ga_product = item.get('ga-product')

        if ga_product:
            try:
                data = json.loads(ga_product)
                name = clean_text(data.get('title', ''))

                if name:
                    return name
            except Exception:
                pass

        name_tag = item.select_one('.title')

        if name_tag:
            name = clean_text(name_tag.get_text())

            if name:
                return name

        img_tag = item.find('img', alt=True)

        if img_tag:
            name = clean_text(img_tag.get('alt', ''))

            if name:
                return name

        return ''

    def get_product_price(self, item):
        price_tag = item.select_one('.quick-cart-price')

        if price_tag:
            return clean_text(price_tag.get_text(' '))

        prices = []

        for tag in item.select('.price, .sl-price'):
            price = clean_text(tag.get_text())

            if price and price not in prices:
                prices.append(price)

        return ' '.join(prices)

    def extract_products_from_page(self, page_data, url):
        products = []

        for item in page_data.select(self.item_selector):
            name = self.get_product_name(item)
            price = self.get_product_price(item)

            if name and price:
                products.append(Product(name=name, price=price))

        return products

    def build_page_url(self, current_url, page_num):
        if page_num == 1:
            return current_url

        return build_url_with_query(current_url, {'page': page_num})

    def get_next_page_url(self, current_url, page_number, page_data):
        return self.build_page_url(current_url, page_number + 1)
