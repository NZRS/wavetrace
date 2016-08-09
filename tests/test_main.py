import unittest
from pathlib import Path 

from wavetrace import *


DATA_DIR = Path(PROJECT_ROOT)/'tests'/'data'

class TestMain(unittest.TestCase):
    def test_get_bounds(self):
        path = DATA_DIR/'test.kml'
        with path.open() as src:
            kml = src.read()

        bounds = get_bounds(kml)
        expect = [173.00000, -38.00000, 177.00000, -35.00083]
        self.assertSequenceEqual(bounds, expect)

if __name__ == '__main__':
    unittest.main()
