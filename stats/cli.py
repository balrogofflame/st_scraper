import argparse
from pathlib import Path

from stats.calculator import calculate_store_stats, get_selected_csv_files, load_store_prices
from stats.exchange_rates import ExchangeRateService
from stats.report_writer import print_results, write_results_to_csv


def build_parser():
    parser = argparse.ArgumentParser(
        description='Calculate mean, median, and standard deviation for store CSV files.'
    )
    parser.add_argument(
        '--input-dir',
        '-d',
        type=Path,
        default=Path('data/items'),
        help='Directory containing CSV files.'
    )
    parser.add_argument(
        '--output-file',
        '-o',
        type=Path,
        default=Path('data/reports/st_stats.csv'),
        help='CSV path for the stats report.'
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='CSV files to include.'
    )
    parser.add_argument(
        '--include',
        '-i',
        nargs='+',
        default=[],
        help='Additional CSV files to include.'
    )
    parser.add_argument(
        '--exclude',
        '-x',
        nargs='+',
        default=[],
        help='CSV files to exclude.'
    )

    return parser


def run_stats(args):
    csv_files = get_selected_csv_files(args)
    exchange_rate_service = ExchangeRateService()

    if not csv_files:
        print('No CSV files selected.')
        return []

    results = []

    for csv_file in csv_files:
        item_prices = load_store_prices(csv_file, exchange_rate_service)
        results.append(calculate_store_stats(Path(csv_file).stem, item_prices))

    print_results(results)
    write_results_to_csv(results, args.output_file)
    print(f'\nSaved stats to {args.output_file}')
    return results


def main():
    parser = build_parser()
    args = parser.parse_args()
    run_stats(args)


if __name__ == '__main__':
    main()
