import base64
import importlib
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from stats.plot_pricing import (
    PNG_FORMAT,
    SPLIT_OUTPUT,
    SVG_FORMAT,
    create_pricing_plot,
    encode_logo_data_uri,
    load_gender_scores,
    load_pricing_points,
    sort_points,
    write_svg_or_png,
)


class PlotPricingTestCase(unittest.TestCase):
    @staticmethod
    def write_test_logo(path, color=(255, 0, 0, 255)):
        image = Image.new('RGBA', (8, 8), color)
        image.save(path)

    def test_load_and_sort_pricing_points(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = root / 'stats.csv'
            logo_dir = root / 'logos'
            schema_path = root / 'gender_imagery_score.csv'
            logo_dir.mkdir()
            self.write_test_logo(logo_dir / 'alpha.png')
            self.write_test_logo(logo_dir / 'beta.png', color=(0, 0, 255, 255))
            csv_path.write_text(
                'Store,Items,Min Mean,Min Median,Min Std Dev,Max Mean,Max Median,Max Std Dev\n'
                'alpha,10,100,90,20,0,0,0\n'
                'beta,20,80,70,10,0,0,0\n',
                encoding='utf-8-sig'
            )
            schema_path.write_text(
                'Store,Gender Score\n'
                'alpha,2\n'
                'beta,-2\n',
                encoding='utf-8-sig'
            )

            points = load_pricing_points(csv_path, logo_dir, schema_path)
            ordered = sort_points(points, 'median')

            self.assertEqual([point.store for point in ordered], ['beta', 'alpha'])
            self.assertEqual([point.gender_score for point in ordered], [-2, 2])

    def test_load_gender_scores(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            schema_path = Path(temp_dir) / 'gender_imagery_score.csv'
            schema_path.write_text(
                'Store,Gender Score\n'
                'alpha,2\n',
                encoding='utf-8-sig'
            )

            self.assertEqual(load_gender_scores(schema_path), {'alpha': 2})

    def test_encode_logo_data_uri_flattens_transparent_background_to_white(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            logo_path = Path(temp_dir) / 'logo.png'
            image = Image.new('RGBA', (2, 1), (0, 0, 0, 0))
            image.putpixel((1, 0), (0, 0, 0, 255))
            image.save(logo_path)

            data_uri = encode_logo_data_uri(logo_path)
            encoded_payload = data_uri.split(',', 1)[1]
            flattened = Image.open(BytesIO(base64.b64decode(encoded_payload)))

            self.assertEqual(flattened.getpixel((0, 0)), (255, 255, 255))
            self.assertEqual(flattened.getpixel((1, 0)), (0, 0, 0))

    def test_create_pricing_plot_outputs_svg(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = root / 'stats.csv'
            logo_dir = root / 'logos'
            schema_path = root / 'gender_imagery_score.csv'
            output_path = root / 'plot.svg'
            logo_dir.mkdir()
            self.write_test_logo(logo_dir / 'alpha.png')
            csv_path.write_text(
                'Store,Items,Min Mean,Min Median,Min Std Dev,Max Mean,Max Median,Max Std Dev\n'
                'alpha,10,100,90,20,0,0,0\n',
                encoding='utf-8-sig'
            )
            schema_path.write_text(
                'Store,Gender Score\n'
                'alpha,2\n',
                encoding='utf-8-sig'
            )

            result_path = create_pricing_plot(csv_path, logo_dir, output_path, gender_schema_file=schema_path)
            svg = result_path.read_text(encoding='utf-8')

            self.assertEqual(result_path, output_path)
            self.assertIn('<svg', svg)
            self.assertIn('alpha', svg)
            self.assertIn('data:image/png;base64,', svg)
            self.assertIn('Gender Imagery Score vs Store Pricing', svg)
            self.assertIn('Gender Imagery vs Price', svg)
            self.assertIn('Mean median:', svg)
            self.assertIn('High pricing', svg)
            self.assertIn('Low pricing', svg)

    def test_create_pricing_plot_outputs_split_svgs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = root / 'stats.csv'
            logo_dir = root / 'logos'
            schema_path = root / 'gender_imagery_score.csv'
            output_path = root / 'plot.svg'
            logo_dir.mkdir()
            self.write_test_logo(logo_dir / 'alpha.png')
            csv_path.write_text(
                'Store,Items,Min Mean,Min Median,Min Std Dev,Max Mean,Max Median,Max Std Dev\n'
                'alpha,10,100,90,20,0,0,0\n',
                encoding='utf-8-sig'
            )
            schema_path.write_text(
                'Store,Gender Score\n'
                'alpha,2\n',
                encoding='utf-8-sig'
            )

            result_paths = create_pricing_plot(
                csv_path,
                logo_dir,
                output_path,
                gender_schema_file=schema_path,
                output_mode=SPLIT_OUTPUT,
                output_format=SVG_FORMAT
            )

            self.assertEqual(
                [path.name for path in result_paths],
                [
                    'plot_store_pricing_dot_plot.svg',
                    'plot_gender_imagery_score_vs_store_pricing.svg',
                    'plot_gender_imagery_vs_price.svg',
                ]
            )

            for path in result_paths:
                self.assertTrue(path.exists())
                self.assertIn('<svg', path.read_text(encoding='utf-8'))

    def test_write_svg_or_png_raises_without_png_dependencies(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / 'plot.png'

            real_import_module = importlib.import_module

            def fake_import_module(name, package=None):
                if name.startswith('svglib') or name.startswith('reportlab'):
                    raise ImportError()
                return real_import_module(name, package)

            with patch('importlib.import_module', side_effect=fake_import_module):
                with self.assertRaisesRegex(RuntimeError, 'svglib'):
                    write_svg_or_png('<svg />', output_path, PNG_FORMAT)

    def test_write_svg_or_png_outputs_png(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / 'plot.png'
            svg_text = (
                '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="30" viewBox="0 0 40 30">'
                '<rect width="40" height="30" fill="#ff6600" />'
                '</svg>'
            )

            result_path = write_svg_or_png(svg_text, output_path, PNG_FORMAT)

            self.assertEqual(result_path, output_path)
            self.assertTrue(output_path.exists())
            self.assertGreater(output_path.stat().st_size, 0)


if __name__ == '__main__':
    unittest.main()
