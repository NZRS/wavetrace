from pathlib import Path 
import re
import csv
import textwrap
import shutil
import subprocess

import requests
from bs4 import BeautifulSoup, SoupStrainer

import wavetrace.utilities as ut

def download_topography_srtm3(srtm_tile_ids, path):
    """
    Download the specified SRTM3 topography tiles from United States 
    National Aeronautics and Space Administration (NASA) and save them
    to the given directory ``path``, creating the directory if it does 
    not exist.

    INPUT:
        - ``srtm_tile_ids``: list of strings; SRTM3 tile names
        - ``path``: string or Path object specifying a directory

    OUTPUT:

        None.

    Download from the United States National Aeronautics and
    Space Administration (NASA) the raster digital surface model data for the 
    given SRTM tile names in 
     and 
    save the files to the directory specified by ``path``, creating the path
    if it does not exist.

    NOTES:
        - The SRTM3 tiles are formatted as `SRTM HGT format <http://www.gdal.org/frmt_various.html#SRTMHGT>`_
        - SRTM3 data is only available between 60 degrees north latitude and 56 degrees south latitude, so tiles given outside of that range will not be downloaded
        - Uses BeautifulSoup to scrape the appropriate NASA webpages
    """
    ext = '.hgt.zip'
    pattern = re.compile(r'^\w+.hgt\.zip$')
    urls = [
      'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/Africa/',
      'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/Australia/',
      'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/Eurasia/',
      'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/Islands/',
      'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/North_America/',
      'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/South_America/',
      ]

    file_names = set(t + ext for t in srtm_tile_ids)

    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True)

    # Use Beautiful Soup to scrape the page
    strainer = SoupStrainer('a', href=pattern)
    for url in urls:
        # Download data for tiles
        response = requests.get(url)
        if response.status_code != requests.codes.ok:
            raise ValueError('Failed to download data from', url)
        for link in BeautifulSoup(response.content, "html.parser", 
          parse_only=strainer):
            file_name = link.get('href') # NASA uses relative URLs
            if file_name not in file_names:
                continue

            # Download file    
            href = url + file_name
            r = requests.get(href, stream=True)
            if r.status_code != requests.codes.ok:
                raise ValueError('Failed to download file', href)    
            p = path/file_name
            with p.open('wb') as tgt:
                for chunk in r:
                    tgt.write(chunk) 
