import tempfile
import unittest
from pathlib import Path

from stats.plot_pricing import create_pricing_plot, load_gender_scores, load_pricing_points, sort_points


class PlotPricingTestCase(unittest.TestCase):
    def test_load_and_sort_pricing_points(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = root / 'stats.csv'
            logo_dir = root / 'logos'
            schema_path = root / 'gender_schema.csv'
            logo_dir.mkdir()
            (logo_dir / 'alpha.png').write_bytes(b'png')
            (logo_dir / 'beta.png').write_bytes(b'png')
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
            schema_path = Path(temp_dir) / 'gender_schema.csv'
            schema_path.write_text(
                'Store,Gender Score\n'
                'alpha,2\n',
                encoding='utf-8-sig'
            )

            self.assertEqual(load_gender_scores(schema_path), {'alpha': 2})

    def test_create_pricing_plot_outputs_svg(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = root / 'stats.csv'
            logo_dir = root / 'logos'
            schema_path = root / 'gender_schema.csv'
            output_path = root / 'plot.svg'
            logo_dir.mkdir()
            (logo_dir / 'alpha.png').write_bytes(b'png')
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
            self.assertIn('Gender Schema Matrix', svg)


if __name__ == '__main__':
    unittest.main()
