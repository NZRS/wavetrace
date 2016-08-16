import unittest
from pathlib import Path 

from wavetrace import *


class TestUtilities(unittest.TestCase):
    def setUp(self):
        try:
            koordinates_key = get_secret('KOORDINATES_API_KEY')
        except KeyError:
            koordinates_key = None

    def test_get_bounds(self):
        lon_lats = [(-11, 9), (0, 11), (5, -8)]
        get = get_bounds(lon_lats)
        expect = [-11, -8, 5, 11]
        self.assertSequenceEqual(get, expect)

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
        lon_lats = [(-1.1, 0.9), (-1.1, 0.9), (1.1, 1.1), (0.5, -0.9)]
        get = get_srtm_tile_ids(lon_lats)
        expect = ['N00W002', 'N01E001', 'S01E000']
        self.assertCountEqual(get, expect)

    def test_get_nzsos_tile_id(self):
        get = get_nzsos_tile_id(1, 3.64)
        self.assertIsNone(get)

        get = get_nzsos_tile_id(174.6964, -36.9245)
        expect = '05'
        self.assertEqual(get, expect)

    def test_get_nzsos_tile_ids(self):
        lon_lats = [(-1.1, 0.9), (174.6964, -36.9245), (172.309, -42.407)]
        get = get_nzsos_tile_ids(lon_lats)
        expect = [None, '05', '18']
        self.assertCountEqual(get, expect)


if __name__ == '__main__':
    unittest.main()
