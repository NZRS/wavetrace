import unittest
from pathlib import Path 

from wavetrace import *


class TestUtilities(unittest.TestCase):

    def test_get_srtm_tile_name(self):
        get = get_srtm_tile_name(27.5, 3.64)
        expect = 'N04E028'
        self.assertEqual(get, expect)

        get = get_srtm_tile_name(27.5, -3.64)
        expect = 'S04E028'
        self.assertEqual(get, expect)

        get = get_srtm_tile_name(-27.5, 3.64)
        expect = 'N04W028'
        self.assertEqual(get, expect)

        get = get_srtm_tile_name(-27.5, -3.64)
        expect = 'S04W028'
        self.assertEqual(get, expect)

    def test_get_srtm_tile_names(self):
        bounds = [-1.1, -0.9, 0.9, 1.1]
        get = get_srtm_tile_names(bounds)
        expect = ['S01W002', 'N00W002', 'N01W002', 'S01W001', 
          'N00W001', 'N01W001', 'S01E000', 'N00E000', 'N01E000']
        self.assertSequenceEqual(get, expect)


if __name__ == '__main__':
    unittest.main()
