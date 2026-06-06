import re


PRICE_PATTERN = re.compile(r'(NT\$|TWD|EUR|USD|€|\$)\s*([\d,]+(?:\.\d+)?)', re.IGNORECASE)
CURRENCY_MAP = {
    'NT$': 'TWD',
    'TWD': 'TWD',
    'EUR': 'EUR',
    '€': 'EUR',
    'USD': 'USD',
    '$': 'USD'
}


def extract_prices(price_text, exchange_rate_service):
    prices = []

    for currency_symbol, raw_value in PRICE_PATTERN.findall(price_text or ''):
        currency_code = CURRENCY_MAP[currency_symbol.upper()]
        amount = float(raw_value.replace(',', ''))
        prices.append(exchange_rate_service.convert_amount_to_target(amount, currency_code))

    return prices


def extract_min_price(price_text, exchange_rate_service):
    prices = extract_prices(price_text, exchange_rate_service)

    if not prices:
        return None

    return min(prices)


def extract_max_price(price_text, exchange_rate_service):
    prices = extract_prices(price_text, exchange_rate_service)

    if not prices:
        return None

    return max(prices)
