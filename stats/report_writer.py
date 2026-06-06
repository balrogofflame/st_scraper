import csv
from pathlib import Path


def format_number(value):
    if isinstance(value, int):
        return str(value)

    if float(value).is_integer():
        return str(int(value))

    return f'{value:.2f}'


def print_results(results):
    headers = [
        'Store',
        'Items',
        'Min Mean',
        'Min Median',
        'Min Std Dev',
        'Max Mean',
        'Max Median',
        'Max Std Dev'
    ]
    rows = []

    for result in results:
        rows.append([
            result.store,
            str(result.items),
            format_number(result.min_mean),
            format_number(result.min_median),
            format_number(result.min_std_dev),
            format_number(result.max_mean),
            format_number(result.max_median),
            format_number(result.max_std_dev)
        ])

    widths = [
        max(len(headers[index]), max((len(row[index]) for row in rows), default=0))
        for index in range(len(headers))
    ]

    header_line = '  '.join(headers[index].ljust(widths[index]) for index in range(len(headers)))
    divider_line = '  '.join('-' * widths[index] for index in range(len(headers)))

    print(header_line)
    print(divider_line)

    for row in rows:
        print('  '.join(row[index].ljust(widths[index]) for index in range(len(headers))))


def write_results_to_csv(results, output_file):
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                'Store',
                'Items',
                'Min Mean',
                'Min Median',
                'Min Std Dev',
                'Max Mean',
                'Max Median',
                'Max Std Dev'
            ],
            lineterminator='\n'
        )
        writer.writeheader()

        for result in results:
            writer.writerow({
                'Store': result.store,
                'Items': result.items,
                'Min Mean': format_number(result.min_mean),
                'Min Median': format_number(result.min_median),
                'Min Std Dev': format_number(result.min_std_dev),
                'Max Mean': format_number(result.max_mean),
                'Max Median': format_number(result.max_median),
                'Max Std Dev': format_number(result.max_std_dev)
            })
