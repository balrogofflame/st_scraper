import csv
from pathlib import Path


PRODUCT_FIELDNAMES = ['Product Name', 'Price']


def ensure_directory(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def write_products_csv(output_path, products):
    output_path = Path(output_path)
    ensure_directory(output_path.parent)

    with output_path.open('w', newline='', encoding='utf-8-sig') as handle:
        if products:
            writer = csv.DictWriter(
                handle,
                fieldnames=PRODUCT_FIELDNAMES,
                lineterminator='\n'
            )
            writer.writeheader()

            for product in products:
                writer.writerow({
                    'Product Name': product.name,
                    'Price': product.price
                })
        else:
            writer = csv.writer(handle, lineterminator='\n')
            writer.writerow(PRODUCT_FIELDNAMES)
            writer.writerow(['No data fetched', ''])
