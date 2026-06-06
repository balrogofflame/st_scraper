import argparse
import base64
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape


@dataclass(frozen=True)
class PricingPoint:
    store: str
    items: int
    min_mean: float
    min_median: float
    min_std_dev: float
    logo_path: Path
    gender_score: int | None = None


def build_parser():
    parser = argparse.ArgumentParser(
        description='Create an SVG pricing plot from st_stats.csv and store logos.'
    )
    parser.add_argument(
        '--input-file',
        '-i',
        type=Path,
        default=Path('data/reports/st_stats.csv'),
        help='Input stats CSV file.'
    )
    parser.add_argument(
        '--logo-dir',
        '-l',
        type=Path,
        default=Path('assets/store_logos'),
        help='Directory containing store logo PNG files.'
    )
    parser.add_argument(
        '--gender-schema-file',
        '-g',
        type=Path,
        default=Path('config/gender_schema.csv'),
        help='CSV file containing store gender schema scores.'
    )
    parser.add_argument(
        '--output-file',
        '-o',
        type=Path,
        default=Path('data/reports/store_pricing_min.svg'),
        help='Output SVG file.'
    )
    parser.add_argument(
        '--sort-by',
        choices=['median', 'mean', 'items'],
        default='median',
        help='How to order stores in the top chart.'
    )
    return parser


def load_gender_scores(schema_file):
    schema_path = Path(schema_file)

    if not schema_path.exists():
        return {}

    scores = {}

    with schema_path.open('r', newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)

        for row in reader:
            store = (row.get('Store') or '').strip().lower()
            score = (row.get('Gender Score') or '').strip()

            if store and score:
                scores[store] = int(score)

    return scores


def load_pricing_points(input_file, logo_dir, gender_schema_file=Path('config/gender_schema.csv')):
    points = []
    gender_scores = load_gender_scores(gender_schema_file)

    with Path(input_file).open('r', newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)

        for row in reader:
            store = (row.get('Store') or '').strip()

            if not store:
                continue

            points.append(PricingPoint(
                store=store,
                items=int(float(row['Items'])),
                min_mean=float(row['Min Mean']),
                min_median=float(row['Min Median']),
                min_std_dev=float(row['Min Std Dev']),
                logo_path=Path(logo_dir) / f'{store}.png',
                gender_score=gender_scores.get(store.lower())
            ))

    return points


def sort_points(points, sort_by):
    if sort_by == 'mean':
        return sorted(points, key=lambda point: point.min_mean)

    if sort_by == 'items':
        return sorted(points, key=lambda point: point.items, reverse=True)

    return sorted(points, key=lambda point: point.min_median)


def encode_logo_data_uri(logo_path):
    if not logo_path.exists():
        return None

    encoded = base64.b64encode(logo_path.read_bytes()).decode('ascii')
    return f'data:image/png;base64,{encoded}'


def currency_label(value):
    return f'NT${int(round(value)):,}'


def log_position(value, min_value, max_value, left, width):
    value = max(value, 1)
    min_log = math.log10(max(min_value, 1))
    max_log = math.log10(max(max_value, 1))

    if math.isclose(min_log, max_log):
        return left + width / 2

    return left + ((math.log10(value) - min_log) / (max_log - min_log)) * width


def build_ticks(min_value, max_value):
    min_power = math.floor(math.log10(max(min_value, 1)))
    max_power = math.ceil(math.log10(max(max_value, 1)))
    ticks = []

    for power in range(min_power, max_power + 1):
        for factor in (1, 2, 5):
            value = factor * (10 ** power)

            if min_value <= value <= max_value:
                ticks.append(value)

    ticks.extend([min_value, max_value])
    return sorted(set(ticks))


def append_shared_styles(parts):
    parts.extend([
        '<style>',
        'text { font-family: "Segoe UI", Arial, sans-serif; fill: #18212b; }',
        '.title { font-size: 28px; font-weight: 700; }',
        '.section-title { font-size: 22px; font-weight: 700; }',
        '.subtitle { font-size: 14px; fill: #536171; }',
        '.axis { stroke: #9aa6b2; stroke-width: 1; }',
        '.tick { stroke: #d7dde4; stroke-width: 1; }',
        '.row-line { stroke: #eef2f6; stroke-width: 1; }',
        '.store { font-size: 16px; font-weight: 700; }',
        '.meta { font-size: 12px; fill: #617182; }',
        '.legend { font-size: 13px; fill: #445160; }',
        '.band { stroke: #9dc5bb; stroke-width: 8; stroke-linecap: round; opacity: 0.9; }',
        '.mean { fill: #0b6e4f; }',
        '.median { fill: #f05d23; }',
        '.value { font-size: 12px; fill: #445160; }',
        '.matrix-link { stroke: #7aa7a0; stroke-width: 2; opacity: 0.85; }',
        '.matrix-column { fill: #f4efe4; }',
        '.matrix-label { font-size: 12px; fill: #536171; }',
        '.matrix-store { font-size: 11px; fill: #445160; }',
        '</style>',
    ])


def build_price_range_values(points):
    all_values = []

    for point in points:
        all_values.extend([
            max(point.min_mean - point.min_std_dev, 1),
            point.min_mean,
            point.min_median,
            point.min_mean + point.min_std_dev
        ])

    return min(all_values), max(all_values)


def append_top_dot_plot(parts, points, chart_left, chart_width, top_margin):
    row_height = 72
    chart_top = top_margin
    chart_bottom = chart_top + row_height * len(points)
    chart_right = chart_left + chart_width
    min_value, max_value = build_price_range_values(points)
    ticks = build_ticks(min_value, max_value)

    parts.extend([
        f'<text class="title" x="{chart_left}" y="42">Store Pricing Comparison</text>',
        f'<text class="subtitle" x="{chart_left}" y="68">Top chart: minimum-price dot plot by store. Green band is mean +/- std dev, green dot is mean, orange dot is median.</text>',
    ])

    for tick in ticks:
        x = log_position(tick, min_value, max_value, chart_left, chart_width)
        parts.append(f'<line class="tick" x1="{x:.2f}" y1="{chart_top}" x2="{x:.2f}" y2="{chart_bottom}" />')
        parts.append(f'<text class="meta" x="{x:.2f}" y="{chart_bottom + 28}" text-anchor="middle">{escape(currency_label(tick))}</text>')

    parts.append(f'<line class="axis" x1="{chart_left}" y1="{chart_bottom}" x2="{chart_right}" y2="{chart_bottom}" />')

    legend_x = chart_right - 290
    legend_y = 42
    parts.extend([
        f'<line class="band" x1="{legend_x}" y1="{legend_y}" x2="{legend_x + 42}" y2="{legend_y}" />',
        f'<circle class="mean" cx="{legend_x + 14}" cy="{legend_y}" r="6" />',
        f'<circle class="median" cx="{legend_x + 32}" cy="{legend_y}" r="6" />',
        f'<text class="legend" x="{legend_x + 56}" y="{legend_y + 5}">Mean +/- Std Dev, Mean, Median</text>',
    ])

    for index, point in enumerate(points):
        y = chart_top + row_height * index + row_height / 2
        row_top = chart_top + row_height * index
        parts.append(f'<line class="row-line" x1="{chart_left}" y1="{row_top}" x2="{chart_right}" y2="{row_top}" />')

        lower = max(point.min_mean - point.min_std_dev, 1)
        upper = point.min_mean + point.min_std_dev
        lower_x = log_position(lower, min_value, max_value, chart_left, chart_width)
        mean_x = log_position(point.min_mean, min_value, max_value, chart_left, chart_width)
        median_x = log_position(point.min_median, min_value, max_value, chart_left, chart_width)
        upper_x = log_position(upper, min_value, max_value, chart_left, chart_width)

        logo_data_uri = encode_logo_data_uri(point.logo_path)

        if logo_data_uri:
            parts.append(
                f'<image href="{logo_data_uri}" x="26" y="{y - 22:.2f}" width="52" height="44" preserveAspectRatio="xMidYMid meet" />'
            )

        parts.append(f'<text class="store" x="92" y="{y - 4:.2f}">{escape(point.store)}</text>')
        parts.append(
            f'<text class="meta" x="92" y="{y + 16:.2f}">'
            f'{point.items} items | mean {escape(currency_label(point.min_mean))} | '
            f'median {escape(currency_label(point.min_median))} | '
            f'std dev {escape(currency_label(point.min_std_dev))}'
            '</text>'
        )
        parts.append(f'<line class="band" x1="{lower_x:.2f}" y1="{y:.2f}" x2="{upper_x:.2f}" y2="{y:.2f}" />')
        parts.append(f'<circle class="mean" cx="{mean_x:.2f}" cy="{y:.2f}" r="7" />')
        parts.append(f'<circle class="median" cx="{median_x:.2f}" cy="{y:.2f}" r="7" />')
        parts.append(
            f'<text class="value" x="{upper_x + 10:.2f}" y="{y + 4:.2f}">{escape(currency_label(point.min_median))}</text>'
        )

    parts.append(f'<line class="row-line" x1="{chart_left}" y1="{chart_bottom}" x2="{chart_right}" y2="{chart_bottom}" />')
    return chart_bottom


def score_to_x(score, left, width):
    return left + ((score + 2) / 4) * width


def position_groups_by_gender(points):
    grouped = {}

    for point in points:
        if point.gender_score is None:
            continue

        grouped.setdefault(point.gender_score, []).append(point)

    positioned = []

    for score, score_points in sorted(grouped.items()):
        ordered_points = sorted(score_points, key=lambda point: (point.min_median, point.store))
        count = len(ordered_points)

        for index, point in enumerate(ordered_points):
            offset = (index - (count - 1) / 2) * 34
            positioned.append((point, offset))

    return positioned


def append_gender_matrix(parts, points, chart_left, chart_width, section_top):
    matrix_points = [point for point in points if point.gender_score is not None]

    if not matrix_points:
        return section_top

    chart_top = section_top + 64
    chart_height = 420
    chart_bottom = chart_top + chart_height
    chart_right = chart_left + chart_width
    min_value = min(min(point.min_mean, point.min_median) for point in matrix_points)
    max_value = max(max(point.min_mean, point.min_median) for point in matrix_points)
    ticks = build_ticks(min_value, max_value)

    parts.extend([
        f'<text class="section-title" x="{chart_left}" y="{section_top}">Gender Schema Matrix</text>',
        f'<text class="subtitle" x="{chart_left}" y="{section_top + 24}">Bottom chart: x-axis is the store gender schema score from -2 (male-leaning) to 2 (female-leaning). Each store shows Min Mean and Min Median.</text>',
    ])

    for score in (-2, -1, 0, 1, 2):
        column_center = score_to_x(score, chart_left, chart_width)
        column_left = column_center - chart_width / 8
        parts.append(
            f'<rect class="matrix-column" x="{column_left:.2f}" y="{chart_top:.2f}" width="{chart_width / 4:.2f}" height="{chart_height:.2f}" opacity="0.32" />'
        )
        parts.append(f'<line class="tick" x1="{column_center:.2f}" y1="{chart_top}" x2="{column_center:.2f}" y2="{chart_bottom}" />')
        parts.append(f'<text class="meta" x="{column_center:.2f}" y="{chart_bottom + 28}" text-anchor="middle">{score}</text>')

    for tick in ticks:
        y = log_position(tick, min_value, max_value, chart_bottom, -chart_height)
        parts.append(f'<line class="tick" x1="{chart_left}" y1="{y:.2f}" x2="{chart_right}" y2="{y:.2f}" />')
        parts.append(f'<text class="meta" x="{chart_left - 16}" y="{y + 4:.2f}" text-anchor="end">{escape(currency_label(tick))}</text>')

    parts.extend([
        f'<line class="axis" x1="{chart_left}" y1="{chart_bottom}" x2="{chart_right}" y2="{chart_bottom}" />',
        f'<line class="axis" x1="{chart_left}" y1="{chart_top}" x2="{chart_left}" y2="{chart_bottom}" />',
        f'<text class="meta" x="{chart_left + chart_width / 2:.2f}" y="{chart_bottom + 54}" text-anchor="middle">Gender schema score</text>',
        f'<text class="meta" x="{chart_left - 88}" y="{chart_top - 18}" text-anchor="start">Minimum price</text>',
    ])

    legend_x = chart_right - 320
    legend_y = section_top + 6
    parts.extend([
        f'<line class="matrix-link" x1="{legend_x}" y1="{legend_y}" x2="{legend_x + 26}" y2="{legend_y}" />',
        f'<circle class="mean" cx="{legend_x + 8}" cy="{legend_y}" r="5" />',
        f'<circle class="median" cx="{legend_x + 20}" cy="{legend_y}" r="5" />',
        f'<text class="legend" x="{legend_x + 40}" y="{legend_y + 4}">Mean and median plotted within each gender-score column</text>',
    ])

    for point, offset in position_groups_by_gender(matrix_points):
        base_x = score_to_x(point.gender_score, chart_left, chart_width) + offset
        mean_y = log_position(point.min_mean, min_value, max_value, chart_bottom, -chart_height)
        median_y = log_position(point.min_median, min_value, max_value, chart_bottom, -chart_height)
        mid_y = (mean_y + median_y) / 2
        logo_data_uri = encode_logo_data_uri(point.logo_path)

        parts.append(f'<line class="matrix-link" x1="{base_x:.2f}" y1="{mean_y:.2f}" x2="{base_x:.2f}" y2="{median_y:.2f}" />')
        parts.append(f'<circle class="mean" cx="{base_x:.2f}" cy="{mean_y:.2f}" r="6" />')
        parts.append(f'<circle class="median" cx="{base_x:.2f}" cy="{median_y:.2f}" r="6" />')

        if logo_data_uri:
            parts.append(
                f'<image href="{logo_data_uri}" x="{base_x - 15:.2f}" y="{mid_y - 43:.2f}" width="30" height="30" preserveAspectRatio="xMidYMid meet" />'
            )

        parts.append(
            f'<text class="matrix-store" x="{base_x:.2f}" y="{mid_y + 40:.2f}" text-anchor="middle">{escape(point.store)}</text>'
        )

    return chart_bottom


def build_svg(points):
    if not points:
        raise ValueError('No pricing points found.')

    left_margin = 300
    right_margin = 120
    top_margin = 120
    gap_between_sections = 140
    bottom_margin = 90
    chart_width = 980
    dot_plot_height = 72 * len(points)
    matrix_height = 520
    width = left_margin + chart_width + right_margin
    height = top_margin + dot_plot_height + gap_between_sections + matrix_height + bottom_margin
    chart_left = left_margin

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fcf9f3" />',
    ]
    append_shared_styles(parts)

    dot_plot_bottom = append_top_dot_plot(parts, points, chart_left, chart_width, top_margin)
    append_gender_matrix(parts, points, chart_left, chart_width, dot_plot_bottom + gap_between_sections)
    parts.append('</svg>')
    return '\n'.join(parts)


def create_pricing_plot(
    input_file,
    logo_dir,
    output_file,
    sort_by='median',
    gender_schema_file=Path('config/gender_schema.csv')
):
    points = load_pricing_points(input_file, logo_dir, gender_schema_file)
    ordered_points = sort_points(points, sort_by)
    svg = build_svg(ordered_points)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding='utf-8', newline='\n')
    return output_path


def main():
    parser = build_parser()
    args = parser.parse_args()
    output_path = create_pricing_plot(
        input_file=args.input_file,
        logo_dir=args.logo_dir,
        output_file=args.output_file,
        sort_by=args.sort_by,
        gender_schema_file=args.gender_schema_file
    )
    print(f'Saved pricing plot to {output_path}')


if __name__ == '__main__':
    main()
