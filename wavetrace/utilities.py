import os
from functools import wraps
import datetime as dt
import json
from math import ceil, floor
from itertools import product
from shapely.geometry import shape, Point
from pathlib import Path 


PROJECT_ROOT = Path(os.path.abspath(os.path.join(
  os.path.dirname(__file__), '../')))
SECRETS_PATH = PROJECT_ROOT/'secrets.json'
NZSOSDEM_POLYGONS_PATH = PROJECT_ROOT/'data'/'nzsosdem_polygons.geojson'

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
    with secrets_path.open() as src:
        d = json.loads(src.read())
    try:
        return d[secret]
    except KeyError:
        raise ValueError("Set the {0} secrets variable".format(secret))

def check_lonlat(lon, lat):
    """
    Raise a ``ValueError if ``lon`` and ``lat`` do not represent a valid 
    WGS84 longitude-latitude pair.

    INPUT:
        - ``lon``: float
        - ``lat``: float

    OUTPUT:
        None.
    """
    if not (-180 <= lon <= 180):
        raise ValueError('Longitude {!s} is out of bounds'.format(lon))
    if not (-90 <= lat <= 90):
        raise ValueError('Latitude {!s} is out of bounds'.format(lat))

def get_bounds(lon_lats):
    """
    Return a bounding box for the list of WGS84 longitude-latitude pairs

    INPUT:
        - ``lon_lats``: list of WGS84 longitude-latitude pairs (float pairs)

    OUTPUT:
        List of floats of the form  ``[min_lon, min_lat, max_lon, max_lat]``
    """
    lons, lats = zip(*lon_lats)
    return [min(lons), min(lats), max(lons), max(lats)]

def get_srtm_tile_id(lon, lat):
    """
    Return the ID of the SRTM tile that covers the given 
    longitude and latitude. 

    INPUT:
        - ``lon``: float; WGS84 longitude
        - ``lat``: float; WGS84 latitude 

    OUTPUT:
        SRTM tile ID (string)
    

    EXAMPLES:

    >>> get_srtm_tile_id(27.5, 3.64)
    'N04E028'

    NOTES:
        SRTM data for an output tile might not actually exist, e.g. data for the tile N90E000 does not exist in NASA's database. 
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

def get_srtm_tile_ids(lon_lats):
    """
    Return the set of names of SRTM tiles that form a minimal cover of 
    the given longitude-latitude points.

    INPUT:
        - ``lon_lats``: list of WGS84 longitude-latitude pairs (float pairs)

    OUTPUT:
        Set of SRTM tile IDs

    NOTES:
        Calls :func:`get_srtm_tile_id`.
    """
    return set(get_srtm_tile_id(lon, lat) for lon, lat in lon_lats)

def get_nzsosdem_tile_id(lon, lat):
    """
    Return the ID of the NZSoSDEM tile that covers the given 
    longitude and latitude. 
    Return ``None`` if no such tile exists.

    INPUT:
        - ``lon``: float; WGS84 longitude
        - ``lat``: float; WGS84 latitude 

    OUTPUT:
        An NZSoS tile ID (string)

    EXAMPLES:
    
    >>> get_nzsosdem_tile_id(27.5, 3.64)
    
    >>> get_nzsosdem_tile_id(174.6964, -36.9245)
    '05'

    NOTES:
        NZSoSDEM tiles only cover New Zealand
    """
    result = None
    point = Point(lon, lat)
    with NZSOSDEM_POLYGONS_PATH.open() as src:
        polys = json.load(src)
        for f in polys['features']:
            polygon = shape(f['geometry'])
            if polygon.contains(point):
                result = f['properties']['tile_id']
                break
    return result

def get_nzsosdem_tile_ids(lon_lats):
    """
    Return the set of names of NZSoSDEM tiles that form a minimal cover of 
    the given longitude-latitude points.

    INPUT:
        - ``lon_lats``: list of float pairs; WGS84 longitude-latitude pairs 

    OUTPUT:
        A set of NZSoSDEM tile names (strings)

    NOTES:
        Calls :func:`get_nzsosdem_tile_id`.
    """
    return set(get_nzsosdem_tile_id(lon, lat) for lon, lat in lon_lats)
