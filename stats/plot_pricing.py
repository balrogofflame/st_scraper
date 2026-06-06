import argparse
import base64
import builtins
import contextlib
import csv
import importlib
import io
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from PIL import Image
from xml.sax.saxutils import escape

SVG_FORMAT = 'svg'
PNG_FORMAT = 'png'
COMBINED_OUTPUT = 'combined'
SPLIT_OUTPUT = 'split'


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
        '--gender-imagery-score-file',
        '-g',
        type=Path,
        default=Path('config/gender_imagery_score.csv'),
        help='CSV file containing store gender imagery scores.'
    )
    parser.add_argument(
        '--output-file',
        '-o',
        type=Path,
        default=Path('data/reports/store_pricing_min.svg'),
        help='Output file or base file name.'
    )
    parser.add_argument(
        '--output-mode',
        choices=[COMBINED_OUTPUT, SPLIT_OUTPUT],
        default=COMBINED_OUTPUT,
        help='Write all plots into one file or split them into multiple files.'
    )
    parser.add_argument(
        '--output-format',
        choices=[SVG_FORMAT, PNG_FORMAT],
        default=SVG_FORMAT,
        help='Output image format.'
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


def load_pricing_points(input_file, logo_dir, gender_schema_file=Path('config/gender_imagery_score.csv')):
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

    with Image.open(logo_path) as source_image:
        rgba_image = source_image.convert('RGBA')
        white_background = Image.new('RGBA', rgba_image.size, (255, 255, 255, 255))
        flattened_image = Image.alpha_composite(white_background, rgba_image).convert('RGB')
        buffer = io.BytesIO()
        flattened_image.save(buffer, format='PNG')

    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
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


def linear_position(value, min_value, max_value, start, length):
    if math.isclose(min_value, max_value):
        return start + length / 2

    return start + ((value - min_value) / (max_value - min_value)) * length


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
        '.map-axis { stroke: #18212b; stroke-width: 5; }',
        '.map-grid { stroke: #e4e9ee; stroke-width: 1; }',
        '.map-label { font-size: 13px; fill: #445160; font-weight: 600; }',
        '.map-value { font-size: 12px; fill: #536171; }',
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
        f'<text class="subtitle" x="{chart_left}" y="68">Minimum-price dot plot by store. Green band is mean +/- std dev, green dot is mean, orange dot is median.</text>',
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
        f'<text class="section-title" x="{chart_left}" y="{section_top}">Gender Imagery Score vs Store Pricing</text>',
        f'<text class="subtitle" x="{chart_left}" y="{section_top + 24}">X-axis is the store gender imagery score from -2 (male-leaning) to 2 (female-leaning). Each store shows Min Mean and Min Median.</text>',
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
        f'<text class="meta" x="{chart_left + chart_width / 2:.2f}" y="{chart_bottom + 54}" text-anchor="middle">Gender imagery score</text>',
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


def append_brand_perceptual_map(parts, points, chart_left, chart_width, section_top):
    map_points = [point for point in points if point.gender_score is not None]

    if not map_points:
        return section_top

    chart_top = section_top + 84
    chart_height = 520
    chart_bottom = chart_top + chart_height
    chart_right = chart_left + chart_width
    x_min = -2.5
    x_max = 2.5
    min_median = min(point.min_median for point in map_points)
    max_median = max(point.min_median for point in map_points)
    mean_median = sum(point.min_median for point in map_points) / len(map_points)
    y_min = max(min_median * 0.8, 1)
    y_max = max(max_median * 1.15, mean_median * 1.1)
    y_ticks = build_ticks(y_min, y_max)
    origin_x = linear_position(0, x_min, x_max, chart_left, chart_width)
    origin_y = log_position(mean_median, y_min, y_max, chart_bottom, -chart_height)
    logo_size = 76

    parts.extend([
        f'<text class="section-title" x="{chart_left}" y="{section_top}">Gender Imagery vs Price</text>',
        f'<text class="subtitle" x="{chart_left}" y="{section_top + 24}">Logo perceptual map. X shows gender imagery score, Y shows minimum median price on a log scale, with the horizontal axis set at the mean minimum median.</text>',
    ])

    for score in (-2, -1, 0, 1, 2):
        x = linear_position(score, x_min, x_max, chart_left, chart_width)
        parts.append(f'<line class="map-grid" x1="{x:.2f}" y1="{chart_top}" x2="{x:.2f}" y2="{chart_bottom}" />')
        parts.append(f'<text class="map-value" x="{x:.2f}" y="{chart_bottom + 28}" text-anchor="middle">{score}</text>')

    for tick in y_ticks:
        y = log_position(tick, y_min, y_max, chart_bottom, -chart_height)
        parts.append(f'<line class="map-grid" x1="{chart_left}" y1="{y:.2f}" x2="{chart_right}" y2="{y:.2f}" />')
        parts.append(
            f'<text class="map-value" x="{chart_left - 16}" y="{y + 4:.2f}" text-anchor="end">{escape(currency_label(tick))}</text>'
        )

    parts.extend([
        f'<line class="map-axis" x1="{chart_left}" y1="{origin_y:.2f}" x2="{chart_right}" y2="{origin_y:.2f}" />',
        f'<line class="map-axis" x1="{origin_x:.2f}" y1="{chart_bottom}" x2="{origin_x:.2f}" y2="{chart_top}" />',
        f'<text class="map-label" x="{chart_left}" y="{origin_y - 14:.2f}" text-anchor="start">Male-leaning imagery</text>',
        f'<text class="map-label" x="{chart_right}" y="{origin_y - 14:.2f}" text-anchor="end">Female-leaning imagery</text>',
        f'<text class="map-label" x="{origin_x + 14:.2f}" y="{chart_top + 14:.2f}" text-anchor="start">High pricing</text>',
        f'<text class="map-label" x="{origin_x + 14:.2f}" y="{chart_bottom - 10:.2f}" text-anchor="start">Low pricing</text>',
        f'<text class="map-value" x="{chart_left + chart_width / 2:.2f}" y="{chart_bottom + 54}" text-anchor="middle">Gender imagery score</text>',
        f'<text class="map-value" x="{origin_x + 14:.2f}" y="{chart_top - 20:.2f}" text-anchor="start">Minimum median price (log scale)</text>',
        f'<text class="map-value" x="{origin_x + 14:.2f}" y="{origin_y + 20:.2f}" text-anchor="start">Mean median: {escape(currency_label(mean_median))}</text>',
    ])

    for point in map_points:
        logo_data_uri = encode_logo_data_uri(point.logo_path)

        if not logo_data_uri:
            continue

        x = linear_position(point.gender_score, x_min, x_max, chart_left, chart_width)
        y = log_position(point.min_median, y_min, y_max, chart_bottom, -chart_height)

        parts.append(
            f'<image href="{logo_data_uri}" x="{x - logo_size / 2:.2f}" y="{y - logo_size / 2:.2f}" '
            f'width="{logo_size}" height="{logo_size}" preserveAspectRatio="xMidYMid meet" />'
        )

    return chart_bottom


def build_svg_document(width, height):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fcf9f3" />',
    ]
    append_shared_styles(parts)
    return parts


def build_combined_svg(points):
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
    perceptual_map_height = 620
    width = left_margin + chart_width + right_margin
    height = (
        top_margin
        + dot_plot_height
        + gap_between_sections
        + matrix_height
        + gap_between_sections
        + perceptual_map_height
        + bottom_margin
    )
    chart_left = left_margin

    parts = build_svg_document(width, height)

    dot_plot_bottom = append_top_dot_plot(parts, points, chart_left, chart_width, top_margin)
    gender_matrix_bottom = append_gender_matrix(
        parts,
        points,
        chart_left,
        chart_width,
        dot_plot_bottom + gap_between_sections
    )
    append_brand_perceptual_map(
        parts,
        points,
        chart_left,
        chart_width,
        gender_matrix_bottom + gap_between_sections
    )
    parts.append('</svg>')
    return '\n'.join(parts)


def build_top_plot_svg(points):
    if not points:
        raise ValueError('No pricing points found.')

    left_margin = 300
    right_margin = 120
    top_margin = 120
    bottom_margin = 90
    chart_width = 980
    dot_plot_height = 72 * len(points)
    width = left_margin + chart_width + right_margin
    height = top_margin + dot_plot_height + bottom_margin
    chart_left = left_margin
    parts = build_svg_document(width, height)
    append_top_dot_plot(parts, points, chart_left, chart_width, top_margin)
    parts.append('</svg>')
    return '\n'.join(parts)


def build_gender_matrix_svg(points):
    matrix_points = [point for point in points if point.gender_score is not None]

    if not matrix_points:
        return None

    left_margin = 300
    right_margin = 120
    top_margin = 80
    bottom_margin = 90
    chart_width = 980
    width = left_margin + chart_width + right_margin
    chart_left = left_margin
    parts = build_svg_document(width, 1)
    bottom = append_gender_matrix(parts, points, chart_left, chart_width, top_margin)
    height = bottom + bottom_margin
    parts[0] = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    parts.append('</svg>')
    return '\n'.join(parts)


def build_brand_perceptual_map_svg(points):
    map_points = [point for point in points if point.gender_score is not None]

    if not map_points:
        return None

    left_margin = 300
    right_margin = 120
    top_margin = 80
    bottom_margin = 90
    chart_width = 980
    width = left_margin + chart_width + right_margin
    chart_left = left_margin
    parts = build_svg_document(width, 1)
    bottom = append_brand_perceptual_map(parts, points, chart_left, chart_width, top_margin)
    height = bottom + bottom_margin
    parts[0] = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    parts.append('</svg>')
    return '\n'.join(parts)


def build_plot_documents(points, output_mode):
    if output_mode == COMBINED_OUTPUT:
        return [('store_pricing_min', build_combined_svg(points))]

    documents = [('store_pricing_dot_plot', build_top_plot_svg(points))]
    gender_matrix_svg = build_gender_matrix_svg(points)
    perceptual_map_svg = build_brand_perceptual_map_svg(points)

    if gender_matrix_svg is not None:
        documents.append(('gender_imagery_score_vs_store_pricing', gender_matrix_svg))

    if perceptual_map_svg is not None:
        documents.append(('gender_imagery_vs_price', perceptual_map_svg))

    return documents


def ensure_output_suffix(output_path, output_format):
    normalized_path = Path(output_path)
    suffix = f'.{output_format}'

    if normalized_path.suffix.lower() != suffix:
        return normalized_path.with_suffix(suffix)

    return normalized_path


def build_output_paths(output_file, output_mode, output_format, document_names):
    base_path = ensure_output_suffix(output_file, output_format)

    if output_mode == COMBINED_OUTPUT:
        return [base_path]

    return [
        base_path.with_name(f'{base_path.stem}_{document_name}.{output_format}')
        for document_name in document_names
    ]


@contextlib.contextmanager
def prefer_pycairo_backend():
    blocked_module_names = {'cairocffi'}
    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in blocked_module_names:
            raise ImportError('Force pycairo fallback for reportlab PNG rendering.')

        return real_import(name, globals, locals, fromlist, level)

    modules_to_clear = [
        module_name
        for module_name in tuple(sys.modules)
        if module_name == 'rlPyCairo' or module_name.startswith('rlPyCairo.')
        or module_name == 'reportlab.graphics.renderPM'
    ]
    cached_modules = {module_name: sys.modules[module_name] for module_name in modules_to_clear}

    for module_name in modules_to_clear:
        sys.modules.pop(module_name, None)

    builtins.__import__ = guarded_import

    try:
        yield
    finally:
        builtins.__import__ = real_import

        for module_name in modules_to_clear:
            sys.modules.pop(module_name, None)

        sys.modules.update(cached_modules)


def write_svg_or_png(svg_text, output_path, output_format):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_format == SVG_FORMAT:
        output_path.write_text(svg_text, encoding='utf-8', newline='\n')
        return output_path

    try:
        svglib_module = importlib.import_module('svglib.svglib')
    except ImportError as exc:
        raise RuntimeError(
            'PNG output requires the optional "svglib", "reportlab", and "rlPyCairo" packages in the project environment.'
        ) from exc

    drawing = svglib_module.svg2rlg(io.BytesIO(svg_text.encode('utf-8')))

    if drawing is None:
        raise RuntimeError('Unable to parse SVG content for PNG output.')

    with prefer_pycairo_backend():
        try:
            render_pm_module = importlib.import_module('reportlab.graphics.renderPM')
            render_pm_module.drawToFile(
                drawing,
                str(output_path),
                fmt='PNG',
                backend='rlPyCairo'
            )
        except ImportError as exc:
            raise RuntimeError(
                'PNG output requires the optional "svglib", "reportlab", and "rlPyCairo" packages in the project environment.'
            ) from exc

    return output_path


def create_pricing_plot(
    input_file,
    logo_dir,
    output_file,
    sort_by='median',
    gender_schema_file=Path('config/gender_imagery_score.csv'),
    output_mode=COMBINED_OUTPUT,
    output_format=SVG_FORMAT
):
    points = load_pricing_points(input_file, logo_dir, gender_schema_file)
    ordered_points = sort_points(points, sort_by)
    documents = build_plot_documents(ordered_points, output_mode)
    output_paths = build_output_paths(
        output_file,
        output_mode,
        output_format,
        [document_name for document_name, _ in documents]
    )
    written_paths = []

    for output_path, (_, svg_text) in zip(output_paths, documents):
        written_paths.append(write_svg_or_png(svg_text, output_path, output_format))

    if len(written_paths) == 1:
        return written_paths[0]

    return written_paths


def main():
    parser = build_parser()
    args = parser.parse_args()
    output_path = create_pricing_plot(
        input_file=args.input_file,
        logo_dir=args.logo_dir,
        output_file=args.output_file,
        sort_by=args.sort_by,
        gender_schema_file=args.gender_imagery_score_file,
        output_mode=args.output_mode,
        output_format=args.output_format
    )
    print(f'Saved pricing plot to {output_path}')


if __name__ == '__main__':
    main()
