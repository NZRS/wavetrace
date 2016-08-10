import os
from functools import wraps
import datetime as dt
import json
from math import ceil, floor
from itertools import product

PROJECT_ROOT = os.path.abspath(os.path.join(
  os.path.dirname(__file__), '../'))
SECRETS_PATH = os.path.join(PROJECT_ROOT, 'secrets.json')


def time_it(f):
    """
    Decorate function ``f`` to measure and print elapsed time when executed.
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        t1 = dt.datetime.now()
        print('Timing {!s}...'.format(f.__name__))
        print(t1, '  Began process')
        result = f(*args, **kwargs)
        t2 = dt.datetime.now()
        minutes = (t2 - t1).seconds/60
        print(t2, '  Finished in %.2f min' % minutes)    
        return result
    return wrap

def get_secret(secret, secrets_path=SECRETS_PATH):
    """
    Get the given setting variable or return explicit exception.
    """
    with open(secrets_path) as src:
        d = json.loads(src.read())
    try:
        return d[secret]
    except KeyError:
        raise ValueError("Set the {0} secrets variable".format(secret))

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

def get_bounds(lon_lats):
    """
    INPUTS:

    - ``lon_lats``: list of WGS84 longitude-latitude pairs (float pairs)

    OUTPUTS:

    Return a list of floats of the form 
    ``[min_lon, min_lat, max_lon, max_lat]``, describing the 
    WGS84 bounding box of the given longitude-latitude points.
    """
    lons, lats = zip(*lon_lats)
    return [min(lons), min(lats), max(lons), max(lats)]

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
    'N04E028'

    NOTES:

    SRTM data for an output tile might not actually exist, e.g. data for the 
    tile N90E000 does not exist in NASA's database. 

    """
    check_lonlat(lon, lat)

    floor_lon = abs(floor(lon))
    floor_lat = abs(floor(lat))
    if lon >= 0:
        prefix = 'E'
    else:
        prefix = 'W'
    lon = prefix + '{:03d}'.format(floor_lon)

    if lat >= 0:
        prefix = 'N'
    else:
        prefix = 'S'
    lat = prefix + '{:02d}'.format(floor_lat)

    return lat + lon 

def get_srtm_tile_names(lon_lats, cover_bounds=False):
    """
    INPUTS:

    - ``lon_lats``: list of WGS84 longitude-latitude pairs (float pairs)
    - ``cover_bounds``: boolean;
    list of the form [min_lon, min_lat, max_lon, max_lat],
      where ``min_lon <= max_lon`` are WGS84 longitudes and 
      ``min_lat <= max_lat`` are WGS84 latitudes

    OUTPUTS:

    Return the list of names of SRTM tiles that form a minimal cover of 
    the given longitude-latitude points.
    If ``cover_bounds``, then return instead the names of the SRTM tiles 
    that form a minimal cover of the WGS84 bounding box of the points.

    NOTES:

    Calls :func:`get_srtm_tile_name`.
    """
    if cover_bounds:
        bounds = get_bounds(lon_lats)
        min_lon, min_lat = int(floor(bounds[0])), int(floor(bounds[1]))    
        max_lon, max_lat = int(ceil(bounds[2])), int(ceil(bounds[3]))
        step_size = 1  # degrees 
        lons = range(min_lon, max_lon, step_size)
        lats = range(min_lat, max_lat, step_size)
        lon_lats = product(lons, lats)

    return [get_srtm_tile_name(lon, lat) for lon, lat in lon_lats]

