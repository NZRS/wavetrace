from pathlib import Path 
from math import ceil, floor
import re
import csv
import textwrap
import shutil
import subprocess

import requests
from bs4 import BeautifulSoup, SoupStrainer


NZ_BOUNDS = [165.7, -47.5, 178.7, -33.9]
NZ_NORTH_ISLAND_BOUNDS = [172.5, -41.7, 178.5, -34.3]
NZ_SOUTH_ISLAND_BOUNDS = [166.5, -47.5, 174.6, -40.3]

def check_lonlat(lon, lat):
    """
    INPUTS:

    - ``lon``: float
    - ``lat``: float

    OUTPUTS:

    None.
    Raise a ``ValueError if ``lon`` and ``lat`` do not represent a valid 
    WGS84 longitude-latitude pair.
    """
    if not (-180 <= lon <= 180):
        raise ValueError('Longitude {!s} is out of bounds'.format(lon))
    if not (-90 <= lat <= 90):
        raise ValueError('Latitude {!s} is out of bounds'.format(lat))

def get_srtm_tile_name(lon, lat):
    """
    INPUTS:

    - ``lon``: float; WGS84 longitude
    - ``lat``: float; WGS84 latitude 

    OUTPUT:

    Return the name (string) of the SRTM tile that covers the given 
    longitude and latitude. 

    EXAMPLES:

    >>> get_srtm_tile_name(27.5, 3.64)
    >>> 'N04E028'

    NOTES:

    SRTM data for an output tile might not actually exist, e.g. data for the 
    tile N90E000 does not exist in NASA's database. 

    """
    check_lonlat(lon, lat)

    abs_lon = int(ceil(abs(lon)))
    abs_lat = int(ceil(abs(lat)))
    if lon >= 0:
        prefix = 'E'
    else:
        prefix = 'W'
    lon = prefix + '{:03d}'.format(abs_lon)

    if lat >= 0:
        prefix = 'N'
    else:
        prefix = 'S'
    lat = prefix + '{:02d}'.format(abs_lat)

    return lat + lon 

def get_srtm_tile_names(bounds):
    """
    INPUTS:

    - ``bounds``: list of the form [min_lon, min_lat, max_lon, max_lat],
      where ``min_lon <= max_lon`` are WGS84 longitudes and 
      ``min_lat <= max_lat`` are WGS84 latitudes

    OUTPUTS:

    A list of names of SRTM tiles that cover the longitude-latitude bounding
    box specified by bounds.

    NOTES:

    Calls :func:`get_srtm_tile_name`.
    """
    min_lon, min_lat = int(floor(bounds[0])), int(floor(bounds[1]))    
    max_lon, max_lat = int(ceil(bounds[2])), int(ceil(bounds[3]))
    step_size = 1  # degrees 
    lons = range(min_lon, max_lon, step_size)
    lats = range(min_lat, max_lat, step_size)
    return [get_srtm_tile_name(lon, lat) for lon in lons for lat in lats]

def download_elevation_data_nasa(bounds, path, high_definition=False, 
  username=None, password=None):
    """
    INPUTS:

    - ``bounds``: list of the form [min_lon, min_lat, max_lon, max_lat],
      where ``min_lon <= max_lon`` are WGS84 longitudes and 
      ``min_lat <= max_lat`` are WGS84 latitudes
    - ``path``: string or Path object specifying a directory
    - ``high_definition``: boolean
    - ``username``: string; NASA Earthdata username for high definition files
    - ``password``: string; NASA Earthdata password for high definition files

    OUTPUTS:

    Download from the United States National Aeronautics and
    Space Administration (NASA) raster elevation data for the 
    longitude-latitude box specified by ``bounds`` in 
    `SRTM HGT format <http://www.gdal.org/frmt_various.html#SRTMHGT>`_ and 
    save it to the path specified by ``path``, creating the path
    if it does not exist.
    If ``high_definition``, then the data is formatted as SRTM-1 V2; 
    otherwise it is formatted as SRTM-3.

    NOTES:

    - SRTM data is only available between 60 degrees north latitude and 
      56 degrees south latitude
    - Uses BeautifulSoup to scrape the appropriate NASA webpages
    - Downloading high definition files is not implemented yet, because it requires a `NASA Earthdata account <https://urs.earthdata.nasa.gov/users/new>`_
    """
    if high_definition:
        raise NotImplementedError('Downloading high definition data has not been implemented yet')
        ext = '.SRTMGL1.hgt.zip'
        pattern = re.compile(r'^\w+\.SRTMGL1\.hgt\.zip$')
        urls = ['http://e4ftl01.cr.usgs.gov/SRTM/SRTMGL1.003/2000.02.11/']

    else:
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

    file_names = set(t + ext for t in get_srtm_tile_names(bounds))

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
            href = url + '/' + file_name
            r = requests.get(href, stream=True, auth=(username, password))
            if response.status_code != requests.codes.ok:
                raise ValueError('Failed to download file', href)    
            p = path/file_name
            print('Downloading {!s}...'.format(file_name))
            with p.open('wb') as tgt:
                for chunk in r:
                    tgt.write(chunk) 

def download_elevation_data_linz(bounds, path, high_definition=False):
    """
    For New Zealand only.
    """ 
    pass
