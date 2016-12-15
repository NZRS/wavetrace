import unittest
from pathlib import Path 
from shapely.geometry import Point

from .context import wavetrace
from wavetrace import *


DATA_DIR = PROJECT_ROOT/'tests'/'data'


class TestUtilities(unittest.TestCase):

    def test_check_tile_id(self):
        self.assertIsNone(check_tile_id('N03E027'))
        self.assertRaises(ValueError, check_tile_id, 'n03E027')
        self.assertRaises(ValueError, check_tile_id, 'N93E027')

    def test_get_tile_id(self):
        path = Path('bongo/S36E174.SRTMGL1.hgt.zip')
        get = get_tile_id(path)
        expect = 'S36E174'
        self.assertEqual(get, expect)

    def test_get_covering_tile_id(self):
        get = get_covering_tile_id(27.5, 3.64)
        expect = 'N03E027'
        self.assertEqual(get, expect)

        get = get_covering_tile_id(27.5, -3.64)
        expect = 'S04E027'
        self.assertEqual(get, expect)

        get = get_covering_tile_id(-27.5, 3.64)
        expect = 'N03W028'
        self.assertEqual(get, expect)

        get = get_covering_tile_id(-27.5, -3.64)
        expect = 'S04W028'
        self.assertEqual(get, expect)

    def test_get_bounds(self):
        for precision, delta in [(None, 0), ('SRTM1', 0.5/3600), 
          ('SRTM3', 1.5/3600)]:
            get = get_bounds('N03E027', precision)
            expect = [27 - delta, 3 - delta, 28 + delta, 4 + delta]
            self.assertSequenceEqual(get, expect)

            get = get_bounds('S03E027', precision)
            expect = [27 - delta, -3 - delta, 28 + delta, -2 + delta]
            self.assertSequenceEqual(get, expect)

            get = get_bounds('N03W027', precision)
            expect = [-27 - delta, 3 - delta, -26 + delta, 4 + delta]
            self.assertSequenceEqual(get, expect)

            get = get_bounds('S03W027', precision)
            expect = [-27 - delta, -3 - delta, -26 + delta, -2 + delta]
            self.assertSequenceEqual(get, expect)

    def test_build_feature(self):
        f = build_feature('N03E027')
        # Should have coordinates of a quadrangle
        coords = f['geometry']['coordinates'][0]
        self.assertEqual(len(coords), 5)
        self.assertSequenceEqual(coords[0], coords[-1])

    def test_build_polygon(self):
        p = build_polygon('N03E027')
        # Should have coordinates of a quadrangle
        coords = list(p.exterior.coords)
        self.assertEqual(len(coords), 5)
        self.assertSequenceEqual(coords[0], coords[-1])

    def test_compute_intersecting_tiles(self):
        geometries = [
          Point((174.3, -35.7)), 
          Point((168.6, -45.2)).buffer(1, 1), # square buffer
          ]
        get = compute_intersecting_tiles(geometries)
        expect = ['S36E174', 
          'S45E167', 'S45E168', 'S45E169', 
          'S46E167', 'S46E168', 'S46E169', 
          'S47E168',
          ]
        self.assertCountEqual(get, expect)

    def test_gdalinfo(self):
        path = DATA_DIR/'srtm3'/'S37E175.hgt'
        get = gdalinfo(path)
        expect = {'width': 1201, 'height': 1201, 'center': (175.5, -36.5)}
        self.assertEqual(get, expect)


if __name__ == '__main__':
    unittest.main()
