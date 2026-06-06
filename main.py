import argparse
from pathlib import Path

import scrapers
from core.registry import get_scraper_class, list_scrapers
from stats.cli import run_stats
from stats.plot_pricing import create_pricing_plot


def build_parser():
    parser = argparse.ArgumentParser(description='Run scrapers and stats reports.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    scrape_parser = subparsers.add_parser('scrape', help='Run one or more scrapers.')
    scrape_parser.add_argument(
        'stores',
        nargs='+',
        help='Store names or "all".'
    )
    scrape_parser.add_argument(
        '--output-dir',
        '-o',
        type=Path,
        default=Path('data/items'),
        help='Directory for scraper CSV output.'
    )

    stats_parser = subparsers.add_parser('stats', help='Calculate stats from store CSV files.')
    stats_parser.add_argument(
        '--input-dir',
        '-d',
        type=Path,
        default=Path('data/items'),
        help='Directory containing store CSV files.'
    )
    stats_parser.add_argument(
        '--output-file',
        '-o',
        type=Path,
        default=Path('data/reports/st_stats.csv'),
        help='CSV path for the stats report.'
    )
    stats_parser.add_argument(
        'files',
        nargs='*',
        help='CSV files to include.'
    )
    stats_parser.add_argument(
        '--include',
        '-i',
        nargs='+',
        default=[],
        help='Additional CSV files to include.'
    )
    stats_parser.add_argument(
        '--exclude',
        '-x',
        nargs='+',
        default=[],
        help='CSV files to exclude.'
    )

    plot_parser = subparsers.add_parser('plot-pricing', help='Create a store pricing SVG plot.')
    plot_parser.add_argument(
        '--input-file',
        '-i',
        type=Path,
        default=Path('data/reports/st_stats.csv'),
        help='Input stats CSV file.'
    )
    plot_parser.add_argument(
        '--logo-dir',
        '-l',
        type=Path,
        default=Path('assets/store_logos'),
        help='Directory containing store logo PNG files.'
    )
    plot_parser.add_argument(
        '--gender-schema-file',
        '-g',
        type=Path,
        default=Path('config/gender_schema.csv'),
        help='CSV file containing store gender schema scores.'
    )
    plot_parser.add_argument(
        '--output-file',
        '-o',
        type=Path,
        default=Path('data/reports/store_pricing_min.svg'),
        help='Output SVG file.'
    )
    plot_parser.add_argument(
        '--sort-by',
        choices=['median', 'mean', 'items'],
        default='median',
        help='How to order stores in the chart.'
    )

    return parser


def run_scrapers(store_names, output_dir):
    available_scrapers = list_scrapers()

    if len(store_names) == 1 and store_names[0].lower() == 'all':
        selected_scrapers = available_scrapers
    else:
        selected_scrapers = []

        for store_name in store_names:
            normalized_name = store_name.lower()

            if normalized_name not in available_scrapers:
                raise ValueError(
                    f'Unknown scraper "{store_name}". Available scrapers: '
                    f'{", ".join(available_scrapers)}'
                )

            selected_scrapers.append(normalized_name)

    for store_name in selected_scrapers:
        scraper_class = get_scraper_class(store_name)
        scraper_class(output_dir=output_dir).run()


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == 'scrape':
        run_scrapers(args.stores, args.output_dir)
        return

    if args.command == 'stats':
        run_stats(args)
        return

    if args.command == 'plot-pricing':
        output_path = create_pricing_plot(
            input_file=args.input_file,
            logo_dir=args.logo_dir,
            output_file=args.output_file,
            sort_by=args.sort_by,
            gender_schema_file=args.gender_schema_file
        )
        print(f'Saved pricing plot to {output_path}')
        return


if __name__ == '__main__':
    main()
