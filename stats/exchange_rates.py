import json
from datetime import datetime
from pathlib import Path

import requests

from core.settings import app_config


class ExchangeRateService:
    def __init__(
        self,
        api_key_file=Path('config/exchangerate_api.txt'),
        cache_dir=Path('data/cache/exchange_rates'),
        target_currency='TWD'
    ):
        self.api_key_file = Path(api_key_file)
        self.cache_dir = Path(cache_dir)
        self.target_currency = target_currency
        self.memory_cache = {}
        self.warned_currencies = set()

    def read_api_key(self):
        if not self.api_key_file.exists():
            return ''

        return self.api_key_file.read_text(encoding='utf-8').strip()

    def get_cache_file(self, currency_code):
        return self.cache_dir / f'{currency_code}.json'

    def is_cache_file_fresh(self, cache_file):
        if not cache_file.exists():
            return False

        cache_date = datetime.fromtimestamp(cache_file.stat().st_mtime).date()
        today = datetime.now().date()
        return cache_date == today

    def load_rate_data(self, base_currency):
        if base_currency in self.memory_cache:
            return self.memory_cache[base_currency]

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = self.get_cache_file(base_currency)

        if self.is_cache_file_fresh(cache_file):
            data = json.loads(cache_file.read_text(encoding='utf-8'))
            self.memory_cache[base_currency] = data
            return data

        api_key = self.read_api_key()

        if not api_key and cache_file.exists():
            self.warn_stale_cache_usage(base_currency, cache_file)
            data = json.loads(cache_file.read_text(encoding='utf-8'))
            self.memory_cache[base_currency] = data
            return data

        url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}'

        try:
            response = requests.get(url, timeout=app_config.exchange_rate_timeout)
            response.raise_for_status()
            data = response.json()

            if data.get('result') != 'success':
                raise ValueError(
                    f'Exchange rate API error for {base_currency}: {data.get("result")}'
                )

            cache_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding='utf-8',
                newline='\n'
            )
            self.memory_cache[base_currency] = data
            return data
        except Exception:
            if cache_file.exists():
                self.warn_stale_cache_usage(base_currency, cache_file)
                data = json.loads(cache_file.read_text(encoding='utf-8'))
                self.memory_cache[base_currency] = data
                return data

            raise

    def warn_stale_cache_usage(self, base_currency, cache_file):
        if base_currency in self.warned_currencies:
            return

        cache_date = datetime.fromtimestamp(cache_file.stat().st_mtime).date().isoformat()
        print(
            f'Warning: using stale exchange rate cache for {base_currency} '
            f'from {cache_date}.'
        )
        self.warned_currencies.add(base_currency)

    def convert_amount_to_target(self, amount, currency_code):
        if currency_code == self.target_currency:
            return int(round(amount))

        rate_data = self.load_rate_data(currency_code)
        conversion_rates = rate_data.get('conversion_rates', {})
        conversion_rate = conversion_rates.get(self.target_currency)

        if conversion_rate is None:
            raise ValueError(
                f'Missing {self.target_currency} conversion rate for {currency_code}'
            )

        return int(round(amount * conversion_rate))
