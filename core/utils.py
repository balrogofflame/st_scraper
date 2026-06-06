import json
from typing import Iterable
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup

from core.models import Product


def clean_text(text):
    return ' '.join((text or '').split())


def normalize_url(base_url, url):
    full_url = urljoin(base_url, url)
    parsed = urlparse(full_url)

    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path.rstrip('/'),
        '',
        '',
        ''
    ))


def build_url_with_query(url, updates):
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))

    for key, value in updates.items():
        query[key] = '' if value is None else str(value)

    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        '',
        urlencode(query),
        ''
    ))


def dedupe_products(products: Iterable[Product]):
    unique_products = {}

    for product in products:
        unique_products[product.name] = product

    return list(unique_products.values())


def format_currency_amount(price_value, currency_code):
    try:
        amount = float(price_value)
    except Exception:
        return clean_text(str(price_value))

    if amount.is_integer():
        amount_text = f'{int(amount):,}'
    else:
        amount_text = f'{amount:,.2f}'

    if currency_code == 'TWD':
        return f'NT${amount_text}'

    if currency_code == 'USD':
        return f'${amount_text}'

    if currency_code == 'EUR':
        return f'€{amount_text}'

    return f'{currency_code} {amount_text}'


def iter_json_ld_candidates(soup: BeautifulSoup):
    for script in soup.select('script[type="application/ld+json"]'):
        raw_text = script.string or script.get_text()

        if not raw_text:
            continue

        try:
            data = json.loads(raw_text)
        except Exception:
            continue

        if isinstance(data, dict):
            yield data
            graph = data.get('@graph')

            if isinstance(graph, list):
                for candidate in graph:
                    if isinstance(candidate, dict):
                        yield candidate

        if isinstance(data, list):
            for candidate in data:
                if isinstance(candidate, dict):
                    yield candidate


def extract_json_ld_product(soup: BeautifulSoup):
    for candidate in iter_json_ld_candidates(soup):
        if candidate.get('@type') != 'Product':
            continue

        name = clean_text(candidate.get('name', ''))
        offers = candidate.get('offers', {})

        if isinstance(offers, list):
            offers = offers[0] if offers else {}

        if not isinstance(offers, dict):
            offers = {}

        price = offers.get('price')
        currency_code = clean_text(offers.get('priceCurrency', ''))

        if name and price and currency_code:
            return Product(
                name=name,
                price=format_currency_amount(price, currency_code)
            )

    return None
