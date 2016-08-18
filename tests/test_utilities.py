import unittest
from pathlib import Path 
from shapely.geometry import Point

from wavetrace import *


class TestUtilities(unittest.TestCase):

    def test_get_tile_id(self):
        get = get_tile_id(27.5, 3.64)
        expect = 'N03E027'
        self.assertEqual(get, expect)

        get = get_tile_id(27.5, -3.64)
        expect = 'S04E027'
        self.assertEqual(get, expect)

        get = get_tile_id(-27.5, 3.64)
        expect = 'N03W028'
        self.assertEqual(get, expect)

        get = get_tile_id(-27.5, -3.64)
        expect = 'S04W028'
        self.assertEqual(get, expect)

    def test_get_bounds(self):
        get = get_bounds('N03E027')
        expect = [27, 3, 28, 4]
        self.assertSequenceEqual(get, expect)

        get = get_bounds('S03E027')
        expect = [27, -3, 28, -2]
        self.assertSequenceEqual(get, expect)

        get = get_bounds('N03W027')
        expect = [-27, 3, -26, 4]
        self.assertSequenceEqual(get, expect)

        get = get_bounds('S03W027')
        expect = [-27, -3, -26, -2]
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

    def test_compute_tile_cover(self):
        geometries = [
          Point((174.3, -35.7)), 
          Point((168.6, -45.2)).buffer(1, 1), # square buffer
          ]
        get = compute_tile_cover(geometries)
        expect = ['S36E174', 
          'S45E167', 'S45E168', 'S45E169', 
          'S46E167', 'S46E168', 'S46E169', 
          'S47E168',
          ]
        self.assertCountEqual(get, expect)

if __name__ == '__main__':
    unittest.main()
