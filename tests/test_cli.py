import unittest

import click.testing
from click.testing import CliRunner

from .context import wavetrace
from wavetrace import *
from wavetrace.cli import wavey


DATA_DIR = PROJECT_ROOT/'tests'/'data'
try:
    GITLAB_KEY = get_secret("GITLAB_API_KEY")
except KeyError:
    GITLAB_KEY = ''

class TestCli(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_process_transmitters(self):
        in_path = DATA_DIR/'transmitters.csv'
        out_path = DATA_DIR/'tmp'
        rm_paths(out_path)

        result = self.runner.invoke(wavey, ['process_transmitters', str(in_path),
          str(out_path)])
        self.assertEqual(result.exit_code, 0)

        rm_paths(out_path)

    def test_srtm_nz(self):
        result = self.runner.invoke(wavey, ['srtm_nz'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip(), 
          ' '.join(SRTM_NZ_TILE_IDS).strip()) 

    def test_get_covering_tiles_ids(self):
        path = DATA_DIR/'transmitters.csv'

        result = self.runner.invoke(wavey, ['get_covering_tiles_ids', str(path)])
        self.assertEqual(result.exit_code, 0)

    @unittest.skipIf(not GITLAB_KEY,
      'Requires a Gitlab API access token stored in ``secrets.json`` under the key ``"GITLAB_API_KEY"``')
    def test_download_topography(self):
        tile_ids = SRTM_NZ_TILE_IDS[:2]
        path = DATA_DIR/'tmp'
        rm_paths(path)

        result = self.runner.invoke(wavey, ['download_topography', 
          *tile_ids, str(path), GITLAB_KEY])
        self.assertEqual(result.exit_code, 0)

        result = self.runner.invoke(wavey, ['download_topography', 
          *tile_ids, str(path), 'wrong'])
        self.assertEqual(result.exit_code, -1)

        rm_paths(path)

    def test_process_topography(self):
        in_path = DATA_DIR/'srtm1'
        out_path = DATA_DIR/'tmp'
        rm_paths(out_path)

        result = self.runner.invoke(wavey, ['process_topography', str(in_path),
          str(out_path)])
        self.assertEqual(result.exit_code, 0)

        rm_paths(out_path)

    def test_compute_coverage(self):
        p1 = DATA_DIR
        p2 = DATA_DIR/'tmp_inputs'
        p3 = DATA_DIR/'tmp_outputs'
        rm_paths(p2, p3)
 
        # High definition tests take too long, so skip them
        self.runner.invoke(wavey, ['process_transmitters', 
          str(p1/'transmitters_single.csv'), str(p2)])
        self.runner.invoke(wavey, ['process_topography',
          str(p1/'srtm3'), str(p2)])
        result = self.runner.invoke(wavey, ['compute_coverage', 
          str(p2), str(p3)])
        print(result.exc_info)
        self.assertEqual(result.exit_code, 0)

        rm_paths(p2, p3)        

    def test_compute_satellite_los(self):
        p1 = DATA_DIR/'srtm3'/'S37E175.hgt'
        p2 = DATA_DIR/'tmp_outputs'/'shadow.tif'
        rm_paths(p2.parent)

        result = self.runner.invoke(wavey, ['compute_satellite_los', 
          str(p1), '152', str(p2)])
        print(result.exc_info)
        self.assertEqual(result.exit_code, 0)

        rm_paths(p2.parent)
