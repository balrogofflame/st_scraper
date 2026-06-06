import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from stats.calculator import calculate_store_stats, get_selected_csv_files, load_store_prices
from stats.exchange_rates import ExchangeRateService
from stats.price_parser import extract_max_price, extract_min_price


class FakeExchangeRateService:
    def convert_amount_to_target(self, amount, currency_code):
        if currency_code == 'EUR':
            return int(round(amount * 40))

        if currency_code == 'USD':
            return int(round(amount * 30))

        return int(round(amount))


class StatsTestCase(unittest.TestCase):
    def test_extract_price_range(self):
        service = FakeExchangeRateService()
        price_text = 'NT$990 €20 $10'
        self.assertEqual(extract_min_price(price_text, service), 300)
        self.assertEqual(extract_max_price(price_text, service), 990)

    def test_load_store_prices_and_calculate_stats(self):
        service = FakeExchangeRateService()

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / 'demo.csv'
            csv_path.write_text(
                'Product Name,Price\n'
                'Item A,NT$100\n'
                'Item B,NT$200 NT$300\n',
                encoding='utf-8-sig'
            )

            item_prices = load_store_prices(csv_path, service)
            stats = calculate_store_stats('demo', item_prices)

            self.assertEqual(stats.store, 'demo')
            self.assertEqual(stats.items, 2)
            self.assertEqual(stats.min_mean, 150)
            self.assertEqual(stats.max_mean, 200)

    def test_get_selected_csv_files_supports_names_and_excludes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir)
            (input_dir / 'a.csv').write_text('Product Name,Price\n', encoding='utf-8-sig')
            (input_dir / 'b.csv').write_text('Product Name,Price\n', encoding='utf-8-sig')
            args = SimpleNamespace(
                input_dir=input_dir,
                output_file=Path(temp_dir) / 'report.csv',
                files=['a'],
                include=[],
                exclude=['b']
            )

            selected_files = get_selected_csv_files(args)
            self.assertEqual([path.name for path in selected_files], ['a.csv'])

    def test_exchange_rates_use_stale_cache_without_api_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            api_key_file = root / 'missing_api_key.txt'
            cache_dir = root / 'cache'
            cache_dir.mkdir()
            cache_file = cache_dir / 'EUR.json'
            cache_file.write_text(
                json.dumps({
                    'result': 'success',
                    'conversion_rates': {
                        'TWD': 40
                    }
                }),
                encoding='utf-8'
            )
            stale_timestamp = 946684800
            cache_file.touch()
            import os
            os.utime(cache_file, (stale_timestamp, stale_timestamp))

            service = ExchangeRateService(
                api_key_file=api_key_file,
                cache_dir=cache_dir
            )
            output = io.StringIO()

            with redirect_stdout(output):
                converted_amount = service.convert_amount_to_target(10, 'EUR')

            self.assertEqual(converted_amount, 400)
            self.assertIn('Warning: using stale exchange rate cache for EUR', output.getvalue())


if __name__ == '__main__':
    unittest.main()
