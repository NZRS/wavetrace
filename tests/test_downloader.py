import unittest
from pathlib import Path 
import shutil

from wavetrace import *


DATA_DIR = Path(PROJECT_ROOT)/'tests'/'data'

class TestDownloader(unittest.TestCase):

    def test_download_srtm_nasa(self):
        # Test tiles. Last one is not in NASA dataset.
        tiles = ['S36E174', 'S37E175', 'N00E000'] 
        tmp = DATA_DIR/'tmp'

        # Should download correct files
        download_srtm_nasa3(tiles, tmp, high_definition=False)
        get_names = [f.name for f in tmp.iterdir()]
        expect_names = [t + '.hgt.zip' for t in tiles if t != 'N00E000']
        self.assertCountEqual(get_names, expect_names)

        shutil.rmtree(str(tmp))


if __name__ == '__main__':
    unittest.main()
