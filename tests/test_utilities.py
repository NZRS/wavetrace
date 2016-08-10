import unittest
from pathlib import Path 

from wavetrace import *


class TestUtilities(unittest.TestCase):

    def test_get_bounds(self):
        lon_lats = [(-11, 9), (0, 11), (5, -8)]
        get = get_bounds(lon_lats)
        expect = [-11, -8, 5, 11]
        self.assertSequenceEqual(get, expect)

    def test_get_srtm_tile_name(self):
        get = get_srtm_tile_name(27.5, 3.64)
        expect = 'N03E027'
        self.assertEqual(get, expect)

        get = get_srtm_tile_name(27.5, -3.64)
        expect = 'S04E027'
        self.assertEqual(get, expect)

        get = get_srtm_tile_name(-27.5, 3.64)
        expect = 'N03W028'
        self.assertEqual(get, expect)

        get = get_srtm_tile_name(-27.5, -3.64)
        expect = 'S04W028'
        self.assertEqual(get, expect)

    def test_get_srtm_tile_names(self):
        lon_lats = [(-1.1, 0.9), (-1.1, 0.9), (1.1, 1.1), (0.5, -0.9)]
        get = get_srtm_tile_names(lon_lats, cover_bounds=False)
        expect = ['N00W002', 'N01E001', 'S01E000']
        self.assertCountEqual(get, expect)

        get = get_srtm_tile_names(lon_lats, cover_bounds=True)
        expect = ['S01W002', 'N00W002', 'N01W002', 
          'S01W001', 'N00W001', 'N01W001', 
          'S01E000', 'N00E000', 'N01E000', 
          'S01E001', 'N00E001', 'N01E001']
        self.assertCountEqual(get, expect)


if __name__ == '__main__':
    unittest.main()
