import unittest
from pathlib import Path 
from copy import copy
import shutil

from .context import wavetrace
from wavetrace import *


DATA_DIR = PROJECT_ROOT/'tests'/'data'
try:
    GITLAB_KEY = get_secret("GITLAB_API_KEY")
except KeyError:
    GITLAB_KEY = ''
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

    @unittest.skipIf(not GITLAB_KEY,
      'Requires a Gitlab API access token stored in ``secrets.json`` under the key ``"GITLAB_API_KEY"``')
    def test_download_topography(self):
        # Test tiles. Last one is not in dataset.
        tmp = DATA_DIR/'tmp'

        # Should download correct files
        tiles = ['S36E174', 'S37E175'] 
        for hd, suffix in [(True, '.SRTMGL1.hgt.zip'), 
          (False, '.SRTMGL3.hgt.zip')]:
            rm_paths(tmp)
            download_topography(tiles, path=tmp, high_definition=hd, 
              api_key=GITLAB_KEY)
            get_names = [f.name for f in tmp.iterdir()]
            expect_names = [t + suffix for t in tiles]
            self.assertCountEqual(get_names, expect_names)

        # Should raise ValueError on bad tiles
        tiles = ['S36E174', 'N00E000']
        for hd in [True, False]:
            self.assertRaises(ValueError, download_topography, tile_ids=tiles, 
              path=tmp, high_definition=hd, api_key=GITLAB_KEY)

        rm_paths(tmp)

    def test_read_transmitters(self):
        # Good inputs should yield good outputs
        path = DATA_DIR/'transmitters.csv'
        ts = read_transmitters(path)

        # Should contain the correct number of transmitters
        self.assertEqual(len(ts), 20)

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

    def test_process_transmitters(self):
        in_path = DATA_DIR/'transmitters.csv'
        out_path = DATA_DIR/'tmp'
        rm_paths(out_path)

        process_transmitters(in_path, out_path)

        # Should contain the correct files
        names_get = [f.name for f in out_path.iterdir()]
        names_expect = [t['name'] + suffix
          for t in read_transmitters(in_path)
          for suffix in ['.qth', '.lrp', '.az', '.el']]
        self.assertCountEqual(names_get, names_expect)

        rm_paths(out_path)

    def test_get_lonlats(self):
        ts = [
          {'longitude': 5.6, 'latitude': -20.4},
          {'longitude': 7.6, 'latitude': 18},
          ]
        get = get_lonlats(ts)
        expect = [(5.6, -20.4), (7.6, 18)]
        self.assertSequenceEqual(get, expect)

        self.assertEqual(get_lonlats([]), [])

    def test_process_topography(self):
        out_path = DATA_DIR/'tmp'
        if out_path.exists():
            shutil.rmtree(str(out_path))

        for hd in [False, True]:
            if hd:
                in_path = DATA_DIR/'srtm1'
                names_expect = ['-36:-35:185:186-hd.sdf']
                suffix = '-hd.sdf'
            else:
                in_path = DATA_DIR/'srtm3'
                names_expect = ['-36:-35:185:186.sdf', 
                  '-37:-36:184:185.sdf']

            process_topography(in_path, out_path, 
              high_definition=hd)

            # Should contain the correct files
            names_get = [f.name for f in out_path.iterdir()]
            self.assertCountEqual(names_get, names_expect)

            shutil.rmtree(str(out_path))

    def test_compute_coverage_0(self):
        p1 = DATA_DIR
        p2 = DATA_DIR/'tmp_inputs'
        p3 = DATA_DIR/'tmp_outputs'

        rm_paths(p2, p3)
 
        # High definition tests take too long, so skip them
        process_transmitters(p1/'transmitters_single.csv', p2)
        process_topography( p1/'srtm3', p2)
        compute_coverage_0(p2, p3)

        # Should contain the correct files
        names_get = [f.name for f in p3.iterdir()]
        names_expect = [t['name'] + suffix
          for t in read_transmitters(p1/'transmitters_single.csv')
          for suffix in ['.ppm', '-ck.ppm', '.kml', '-site_report.txt']]
        self.assertCountEqual(names_get, names_expect)

        rm_paths(p2, p3)

    def test_get_bounds_from_kml(self):
        path = DATA_DIR/'test.kml'
        with path.open() as src:
            kml = src.read()

        bounds = get_bounds_from_kml(kml)
        expect = [173.00000, -38.00000, 177.00000, -35.00083]
        self.assertSequenceEqual(bounds, expect)

    def test_postprocess_coverage_0(self):
        p1 = DATA_DIR
        p2 = DATA_DIR/'tmp_inputs'
        p3 = DATA_DIR/'tmp_outputs'
        rm_paths(p2, p3)

        transmitters = read_transmitters(p1/'transmitters_single.csv')
        process_transmitters(p1/'transmitters_single.csv', p2)
        process_topography(p1, p2)
        compute_coverage_0(p2, p3)
        postprocess_coverage_0(p3, keep_ppm=True)

        # Should contain the correct files
        names_get = [f.name for f in p3.iterdir()]
        names_expect = [t['name'] + suffix
          for t in transmitters
          for suffix in ['.ppm', '-ck.ppm', '.kml', '-site_report.txt', 
            '.png', '-ck.png', '.tif']]
        self.assertCountEqual(names_get, names_expect)

        # KML should have PNG references
        for f in p3.iterdir():
            if f.suffix == '.kml':
                with f.open() as src:
                    kml = src.read()
                self.assertTrue('.png' in kml)
                self.assertTrue('.ppm' not in kml)

        rm_paths(p2, p3)

    def test_compute_coverage(self):
        p1 = DATA_DIR
        p2 = DATA_DIR/'tmp_inputs'
        p3 = DATA_DIR/'tmp_outputs'
        rm_paths(p2, p3)
 
        # High definition tests take too long, so skip them
        process_transmitters(p1/'transmitters_single.csv', p2)
        process_topography( p1/'srtm3', p2)
        compute_coverage(p2, p3, keep_ppm=False)

        # Should contain the correct files
        names_get = [f.name for f in p3.iterdir()]
        names_expect = [t['name'] + suffix
          for t in read_transmitters(p1/'transmitters_single.csv')
          for suffix in ['.kml', '-site_report.txt', 
            '.png', '-ck.png', '.tif']]
        self.assertCountEqual(names_get, names_expect)

        rm_paths(p2, p3)

    def test_compute_look_angles(self):
        # Values taken from `Determination of look angles to geostationary communication satellites <https://www.ngs.noaa.gov/CORS/Articles/SolerEisemannJSE.pdf>`_ by Tomas Soler David W. Eisemann.
        expect = {
            0: (180.0000, 38.2164),
            10: (165.9883, 37.2629),
            20: (152.7459, 34.5215),
            30: (140.7453, 30.2941),
            40: (130.0943, 24.9504),
            50: (120.6540, 18.8367),
            60: (112.1789, 12.2358),
            70: (104.4038, 5.3646),
            75: (100.6996, 1.8804),
            77.6865: (98.7453, 0.0034),
            77.6914: (98.7418, 0.0000),
            -10: (194.0117, 37.2629),
            -20: (207.2541, 34.5215),
            -30: (219.2547, 30.2941),
            -40: (229.9057, 24.9504),
            -50: (239.3460, 18.8367),
            -60: (247.8211, 12.2358),
            -70: (255.5962, 5.3646),
            -75: (259.3004, 1.8804),
            -77.6865: (261.2547, 0.0034),
            -77.6914: (261.2582, 0.0000),
        }
        # However, the values above are relative to the GRS80 ellipsoid and not the WGS84 ellipsoid that we are using, so compensate by comparing only a few digits
        decimals = 1
        for lon_s, (az, el) in expect.items():
            print(lon_s, az, el)
            get_az, get_el = compute_look_angles(0, 45, 0, lon_s)
            self.assertAlmostEqual(get_az, az, places=decimals)
            self.assertAlmostEqual(get_el, el, places=decimals)
            
    def test_partition(self):
        n = 3
        subtiles = partition(10, 10, n)
        # Should be the correct length
        self.assertEqual(len(subtiles), n**2)
        # Each subtile item should have the correct length
        self.assertSequenceEqual([len(s) for s in subtiles], 
          [4 for i in range(n**2)])
        # Should be correct on an example subtile
        expect = (6, 0, 4, 3)
        self.assertSequenceEqual(subtiles[2], expect)

    def test_get_geoid_height(self):
        get = get_geoid_height(-3.01, 16.78)
        expect = 28.7069
        self.assertEqual(get, expect)

    def test_compute_satellite_los(self):
        p1 = DATA_DIR/'srtm3'/'S37E175.hgt'
        p2 = DATA_DIR/'tmp_outputs'/'shadow.tif'
        rm_paths(p2.parent)

        compute_satellite_los(p1, 152, p2)
        # Output should exist
        self.assertTrue(p2.exists())
        # Output should have same size and center as input
        self.assertEqual(gdalinfo(p1), gdalinfo(p2))

        rm_paths(p2.parent)


if __name__ == '__main__':
    unittest.main()
