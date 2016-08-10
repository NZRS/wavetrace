import unittest
from pathlib import Path 
from copy import copy
import shutil

from wavetrace import *


DATA_DIR = Path(PROJECT_ROOT)/'tests'/'data'
TRANSMITTER_1 = {
 'antenna_downtilt': '1',
 'antenna_height': 20.0,
 'bearing': '0',
 'frequency': 5725.0,
 'horizontal_beamwidth': '90',
 'latitude': -35.658841,
 'longitude': 174.281534,
 'name': 'MyNetwork_5',
 'network_name': 'My Network',
 'polarization': 0.0,
 'power_eirp': 4.0,
 'site_name': '5',
 'vertical_beamwidth': '30',
 }

class TestMain(unittest.TestCase):

    def test_read_transmitters(self):
        # Good inputs should yield good outputs
        path = DATA_DIR/'transmitters.csv'
        ts = read_transmitters(path)
        float_fields = ['latitude', 'longitude', 'antenna_height', 
          'polarization', 'frequency', 'power_eirp']
        for t in ts:
            # Should contain the required fields
            self.assertTrue(set(REQUIRED_TRANSMITTER_FIELDS) <= set(t.keys()))
            # Should have correct types
            for field in REQUIRED_TRANSMITTER_FIELDS:
                if field in float_fields:
                    self.assertIsInstance(t[field], float)
                else:
                    self.assertIsInstance(t[field], str)

        # Bad header data should raise a ValueError
        path = DATA_DIR/'transmitters_bad_header.csv'
        self.assertRaises(ValueError, read_transmitters, path)

        # Bad values should raise a ValueError
        path = DATA_DIR/'transmitters_bad_values.csv'
        self.assertRaises(ValueError, read_transmitters, path)

    def test_build_transmitter_name(self):
        get = build_transmitter_name('Wa ka w a k a', ' wa ka')
        expect = 'Wakawaka_waka'
        self.assertTrue(get, expect)

        get = build_transmitter_name('Wa ka w a k a', ' ')
        expect = 'Wakawaka_'
        self.assertTrue(get, expect)

    def test_build_splat_qth(self):
        get = build_splat_qth(TRANSMITTER_1)
        # Should have the correct number of lines
        self.assertEqual(len(get.split('\n')), 4)

    def test_build_splat_lrp(self):
        get = build_splat_lrp(TRANSMITTER_1)
        # Should have the correct number of lines
        self.assertEqual(len(get.split('\n')), 9)

    def test_build_splat_az(self):
        get = build_splat_az(TRANSMITTER_1)
        # Should have the correct number of lines
        self.assertEqual(len(get.split('\n')), 361)

        t = copy(TRANSMITTER_1)
        del t['bearing']
        # Should have the correct number of lines
        get = build_splat_az(t)
        # Should have the correct number of lines
        self.assertEqual(len(get.split('\n')), 1)

    def test_build_splat_el(self):
        get = build_splat_el(TRANSMITTER_1)
        # Should have the correct number of lines
        self.assertEqual(len(get.split('\n')), 102)

        t = copy(TRANSMITTER_1)
        del t['bearing']
        # Should have the correct number of lines
        get = build_splat_az(t)
        # Should have the correct number of lines
        self.assertEqual(len(get.split('\n')), 1)

    def test_create_splat_transmitter_files(self):
        in_path = DATA_DIR/'transmitters.csv'
        out_path = DATA_DIR/'tmp'
        create_splat_transmitter_files(in_path, out_path)

        # Should contain the correct files
        names_get = [f.name for f in out_path.iterdir()]
        names_expect = [t['name'] + suffix
          for t in read_transmitters(in_path)
          for suffix in ['.qth', '.lrp', '.az', '.el']]
        self.assertCountEqual(names_get, names_expect)

        shutil.rmtree(str(out_path))

    def test_get_lon_lats(self):
        ts = [
          {'longitude': 5.6, 'latitude': -20.4},
          {'longitude': 7.6, 'latitude': 18},
          ]
        get = get_lon_lats(ts)
        expect = [(5.6, -20.4), (7.6, 18)]
        self.assertSequenceEqual(get, expect)

        self.assertEqual(get_lon_lats([]), [])

    def test_create_splat_topography_files(self):
        in_path = DATA_DIR
        out_path = DATA_DIR/'tmp'
        create_splat_topography_files(in_path, out_path)

        # Should contain the correct files
        names_get = [f.name for f in out_path.iterdir()]
        names_expect = ['-36:-35:185:186.sdf', '-37:-36:184:185.sdf']
        self.assertCountEqual(names_get, names_expect)

        shutil.rmtree(str(out_path))

    def test_create_coverage_reports(self):
        p1 = DATA_DIR
        p2 = DATA_DIR/'tmp_inputs'
        p3 = DATA_DIR/'tmp_outputs'
        create_splat_transmitter_files(p1/'transmitters_single.csv', p2)
        create_splat_topography_files(p1, p2)
        create_coverage_reports(p2, p3)

        # Should contain the correct files
        names_get = [f.name for f in p3.iterdir()]
        names_expect = [t['name'] + suffix
          for t in read_transmitters(p1/'transmitters_single.csv')
          for suffix in ['.ppm', '-ck.ppm', '.kml', '-site_report.txt']]
        self.assertCountEqual(names_get, names_expect)

        shutil.rmtree(str(p2))
        shutil.rmtree(str(p3))

    def test_get_bounds_from_kml(self):
        path = DATA_DIR/'test.kml'
        with path.open() as src:
            kml = src.read()

        bounds = get_bounds_from_kml(kml)
        expect = [173.00000, -38.00000, 177.00000, -35.00083]
        self.assertSequenceEqual(bounds, expect)


if __name__ == '__main__':
    unittest.main()
