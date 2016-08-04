from pathlib import Path 
from math import ceil, floor
import re
import csv
import textwrap

import requests
from bs4 import BeautifulSoup, SoupStrainer


NZ_BOUNDS = [165.7, -47.5, 178.7, -33.9]
NZ_NORTH_ISLAND_BOUNDS = [172.5, -41.7, 178.5, -34.3]
NZ_SOUTH_ISLAND_BOUNDS = [166.5, -47.5, 174.6, -40.3]
TRANSMITTER_REQUIRED_FIELDS = [
  'network_name',    
  'site_name',
  'latitude', # WGS84 float
  'longitude', # WGS84 float 
  'antenna_height', # meters
  'polarization', # 0 (horizontal) or 1 (vertical)
  'frequency', # mega Herz
  'power_eirp', # Watts
  ]
TRANSMITTER_OPTIONAL_FIELDS = [
  'bearing', 
  'horizontal_beamwidth',    
  'vertical_beamwidth',
  'antenna_downtilt',
  ]
# Defaults:
DIALECTRIC_CONSTANT = 15
CONDUCTIVITY = 0.005
RADIO_CLIMATE = 6
FRACTION_OF_TIME = 0.5


def build_transmitter_name(network_name, site_name):
    return network_name.replace(' ', '') + '_' +\
      site_name.replace(' ', '')

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

def download_elevation_data_nasa(bounds, out_dir, high_definition=False):
    """
    INPUTS:

    - ``bounds``: list of the form [min_lon, min_lat, max_lon, max_lat],
      where ``min_lon <= max_lon`` are WGS84 longitudes and 
      ``min_lat <= max_lat`` are WGS84 latitudes
    - ``out_dir``: string or Path object specifying a directory
    - ``high_definition``: boolean

    OUTPUTS:

    Download from the United States National Aeronautics and
    Space Administration (NASA) raster elevation data for the 
    longitude-latitude box specified by ``bounds`` in 
    `SRTM HGT format <http://www.gdal.org/frmt_various.html#SRTMHGT>`_ and 
    save it to the directory specified by ``out_dir``, creating the directory
    if it does not exist.
    If ``high_definition``, then the data is formatted as SRTM-1 V2; 
    otherwise it is formatted as SRTM-3.

    NOTES:

    - SRTM data is only available between 60 degrees north latitude and 
      56 degrees south latitude
    - Uses BeautifulSoup to scrape the appropriate NASA webpages
    """
    if high_definition:
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

    out_dir = Path(out_dir)
    if not out_dir.exists():
        out_dir.mkdir(parents=True)

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
            r = requests.get(href, stream=True)
            if response.status_code != requests.codes.ok:
                raise ValueError('Failed to download file', href)    
            path = out_dir/file_name
            print('Downloading {!s}...'.format(file_name))
            with path.open('wb') as tgt:
                for chunk in r:
                    tgt.write(chunk) 

def download_elevation_data_linz(bounds, out_dir, high_definition=False):
    """
    Relevant only to New Zealand.
    """ 
    pass

def create_splat_elevation_data(in_dir, out_dir, high_definition=False):
    """
    INPUTS:

    - ``in_dir``: string or Path object specifying a directory
    - ``out_dir``: string or Path object specifying a directory
    - ``high_definition``: boolean

    OUTPUTS:

    Convert the SRTM HGT elevation data files in the directory ``in_dir`` to 
    SPLAT! Data File (SDF) files and place the result in the directory
    ``out_dir``, creating the directory if it does not exist.
    If ``high_definition``, then assume the input data is high definition.

    NOTES:

    Uses SPLAT!'s ``srtm2sdf`` or ``srtm2sdf-hd`` (if ``high_definition``) 
    command to do the conversion.
    """
    pass

def read_transmitters(path):
    """
    Return a list of dictionaries, one for each transmitter.
    ...
    """
    path = Path(path)
    transmitters = []
    with path.open() as src:
        reader = csv.DictReader(src)
        header = next(reader) # Skip header
        if not set(TRANSMITTER_REQUIRED_FIELDS) <= set(header.keys()):
            raise ValueError('Transmitter CSV header must contain '\
              'the fields {!s}'.format(TRANSMITTER_REQUIRED_FIELDS))
        for row in reader:
            row['name'] = build_transmitter_name(row['network_name'], 
              row['site_name'])
            transmitters.append(row)
    return transmitters
   
def create_splat_qth_data(transmitters, out_dir):
    """
    """
    out_dir = Path(out_dir)
    if not out_dir.exists():
        out_dir.mkdir(parents=True)
        
    for t in transmitters:
        # Convert to degrees east in range (-360, 0] for SPLAT!
        lon = -float(t['longitude'])
        s = "{!s}\n{!s}\n{!s}\n{!s}m".format(
          t['name'], 
          t['latitude'],
          lon, 
          t['antenna_height'])

        path = Path(out_dir)/'{!s}.qth'.format(t['name'])
        with path.open('w') as tgt:
            tgt.write(s)

def create_splat_lrp_data(transmitters, out_dir, 
  dialectric_constant=DIALECTRIC_CONSTANT, conductivity=CONDUCTIVITY,
  radio_climate=RADIO_CLIMATE, fraction_of_time=FRACTION_OF_TIME):
    """
    """
    out_dir = Path(out_dir)
    if not out_dir.exists():
        out_dir.mkdir(parents=True)

    for t in transmitters:
        s = """\
        {!s} ; Earth Dielectric Constant (Relative permittivity)
        {!s} ; Earth Conductivity (Siemens per meter)
        301.000 ; Atmospheric Bending Constant (N-units)
        {!s} ; Frequency in MHz (20 MHz to 20 GHz)
        {!s} ; Radio Climate
        {!s} ; Polarization (0 = Horizontal, 1 = Vertical)
        0.5 ; Fraction of situations
        {!s} ; Fraction of time 
        {!s} ; ERP in watts""".format(
          dialectric_constant, 
          conductivity, 
          t['frequency'],
          radio_climate, 
          t['polarization'], 
          fraction_of_time,
          t['power_eirp'])
        s = textwrap.dedent(s)

        path = Path(out_dir)/'{!s}.lrp'.format(t['name'])
        with path.open('w') as tgt:
            tgt.write(s)

def create_splat_az_data(transmitters, out_dir):
    pass

def create_splat_el_data(transmitters, out_dir):
    pass


def create_coverage_maps(in_dir, out_dir):
    """
    """
    pass