import unittest
from pathlib import Path 

from wavetrace import *


class TestUtilities(unittest.TestCase):

    def test_get_srtm_tile_id(self):
        get = get_srtm_tile_id(27.5, 3.64)
        expect = 'N03E027'
        self.assertEqual(get, expect)

        get = get_srtm_tile_id(27.5, -3.64)
        expect = 'S04E027'
        self.assertEqual(get, expect)

        get = get_srtm_tile_id(-27.5, 3.64)
        expect = 'N03W028'
        self.assertEqual(get, expect)

        get = get_srtm_tile_id(-27.5, -3.64)
        expect = 'S04W028'
        self.assertEqual(get, expect)

    def test_get_srtm_tile_ids(self):
        lonlats = [(-1.1, 0.9), (-1.1, 0.9), (1.1, 1.1), (0.5, -0.9)]
        get = get_srtm_tile_ids(lonlats)
        expect = ['N00W002', 'N01E001', 'S01E000']
        self.assertCountEqual(get, expect)

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

    def test_get_polygons(self):
        tids = ['N03E027', 'S04E027']
        polygons = get_polygons(tids)
        # Should be correct length
        self.assertEqual(len(polygons), 2)
        # Should have coordinates of a quadrangle
        for p in polygons:
            coords = p['geometry']['coordinates'][0]
            self.assertEqual(len(coords), 5)
            self.assertSequenceEqual(coords[0], coords[-1])


if __name__ == '__main__':
    unittest.main()
