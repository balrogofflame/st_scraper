import csv
from pathlib import Path
from statistics import mean, median, pstdev

from core.models import StoreStats
from stats.price_parser import extract_max_price, extract_min_price


def get_available_csv_files(input_dir, report_output_file=None):
    input_dir = Path(input_dir)

    if not input_dir.exists():
        return []

    report_name = Path(report_output_file).name if report_output_file else None

    return sorted(
        path.resolve() for path in input_dir.glob('*.csv')
        if path.name != report_name
    )


def resolve_csv_targets(targets, available_files, input_dir):
    input_dir = Path(input_dir)
    resolved_files = []
    available_by_name = {path.name.lower(): path for path in available_files}
    available_by_stem = {path.stem.lower(): path for path in available_files}

    for target in targets:
        target_path = Path(target)

        if target_path.exists():
            resolved_files.append(target_path.resolve())
            continue

        input_dir_target = input_dir / target_path

        if input_dir_target.exists():
            resolved_files.append(input_dir_target.resolve())
            continue

        if not target_path.suffix:
            input_dir_csv_target = input_dir / f'{target_path.name}.csv'

            if input_dir_csv_target.exists():
                resolved_files.append(input_dir_csv_target.resolve())
                continue

        normalized_target = target.lower()

        if normalized_target in available_by_name:
            resolved_files.append(available_by_name[normalized_target])
            continue

        if normalized_target in available_by_stem:
            resolved_files.append(available_by_stem[normalized_target])
            continue

        if target_path.suffix.lower() == '.csv':
            resolved_files.append(input_dir_target.resolve())

    unique_files = []
    seen = set()

    for path in resolved_files:
        if path.suffix.lower() == '.csv' and path not in seen:
            unique_files.append(path)
            seen.add(path)

    return unique_files


def get_selected_csv_files(args):
    input_dir = Path(args.input_dir).resolve()
    available_files = get_available_csv_files(input_dir, args.output_file)
    include_targets = list(args.files) + list(args.include)

    if include_targets:
        selected_files = resolve_csv_targets(include_targets, available_files, input_dir)
    else:
        selected_files = available_files

    excluded_files = set(resolve_csv_targets(args.exclude, available_files, input_dir))
    return [path for path in selected_files if path not in excluded_files]


def load_store_prices(csv_file, exchange_rate_service):
    item_prices = []

    with Path(csv_file).open('r', newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)

        for row in reader:
            product_name = (row.get('Product Name') or '').strip()
            price_text = (row.get('Price') or '').strip()
            min_price = extract_min_price(price_text, exchange_rate_service)
            max_price = extract_max_price(price_text, exchange_rate_service)

            if product_name and min_price is not None and max_price is not None:
                item_prices.append({
                    'Product Name': product_name,
                    'Price': price_text,
                    'Min Price': min_price,
                    'Max Price': max_price
                })

    return item_prices


def calculate_store_stats(store_name, item_prices):
    min_prices = [item['Min Price'] for item in item_prices]
    max_prices = [item['Max Price'] for item in item_prices]

    if not min_prices or not max_prices:
        return StoreStats(
            store=store_name,
            items=0,
            min_mean=0,
            min_median=0,
            min_std_dev=0,
            max_mean=0,
            max_median=0,
            max_std_dev=0
        )

    return StoreStats(
        store=store_name,
        items=len(item_prices),
        min_mean=mean(min_prices),
        min_median=median(min_prices),
        min_std_dev=pstdev(min_prices),
        max_mean=mean(max_prices),
        max_median=median(max_prices),
        max_std_dev=pstdev(max_prices)
    )
