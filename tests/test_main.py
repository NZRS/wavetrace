import unittest
from pathlib import Path 

from wavetrace import *


class TestMain(unittest.TestCase):

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



if __name__ == '__main__':
    unittest.main()
