from urllib.parse import urlparse, urlunparse

from core.base_scraper import BaseScraper
from core.models import Product, ScrapeTarget
from core.utils import build_url_with_query, clean_text, normalize_url


class ShoplineJsonScraper(BaseScraper):
    home_url = ''
    products_per_page = 24

    def parse_response(self, response):
        return response.json()

    def get_target_urls(self):
        collection_urls = []
        seen_urls = set()
        soup = self.fetch_page(self.home_url)

        if soup is None:
            return []

        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = normalize_url(self.base_url, href)
            parsed = urlparse(full_url)

            if (
                parsed.netloc == urlparse(self.base_url).netloc
                and '/collections/' in parsed.path
                and full_url not in seen_urls
            ):
                seen_urls.add(full_url)
                collection_urls.append(full_url)

        return [ScrapeTarget(url=url, label='collection', paginate=True) for url in collection_urls]

    def build_collection_api_url(self, collection_url):
        normalized_url = normalize_url(self.home_url, collection_url)
        parsed = urlparse(normalized_url)

        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            f'{parsed.path}/search_products.json',
            '',
            '',
            ''
        ))

    def build_page_url(self, base_url, page_num):
        api_url = base_url

        if not base_url.endswith('search_products.json'):
            api_url = self.build_collection_api_url(base_url)

        return build_url_with_query(api_url, {
            'page': page_num,
            'per': self.products_per_page
        })

    def get_first_page_url(self, target_url):
        return self.build_page_url(target_url, 1)

    def get_next_page_url(self, current_url, page_number, page_data):
        return self.build_page_url(current_url, page_number + 1)

    def format_price(self, value):
        if value is None:
            return ''

        numeric_value = float(value)

        if numeric_value.is_integer():
            return f'NT${int(numeric_value):,}'

        return f'NT${numeric_value:,.2f}'

    def extract_products_from_page(self, page_data, url):
        products = []

        for item in page_data.get('products', []):
            name = clean_text(item.get('title', ''))

            if not name:
                continue

            cheapest_price = item.get('cheapest_variant_price')
            most_expensive_price = item.get('most_expensive_variant_price')
            compare_at_price = item.get('cheapest_variant_compare_at_price')
            prices = []

            if (
                cheapest_price is not None
                and most_expensive_price is not None
                and cheapest_price != most_expensive_price
            ):
                prices.append(
                    f'{self.format_price(cheapest_price)} ~ '
                    f'{self.format_price(most_expensive_price)}'
                )
            elif cheapest_price is not None:
                prices.append(self.format_price(cheapest_price))

            if compare_at_price is not None and compare_at_price not in [
                cheapest_price,
                most_expensive_price
            ]:
                prices.append(self.format_price(compare_at_price))

            price = ' '.join(prices)

            if price:
                products.append(Product(name=name, price=price))

        return products
