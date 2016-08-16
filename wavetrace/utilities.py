import os
from functools import wraps
import datetime as dt
import json
from math import ceil, floor
from itertools import product
from pathlib import Path 


PROJECT_ROOT = Path(os.path.abspath(os.path.join(
  os.path.dirname(__file__), '../')))
SECRETS_PATH = PROJECT_ROOT/'secrets.json'
NZSOSDEM_POLYGONS_PATH = PROJECT_ROOT/'data'/'nzsos_polygons.geojson'

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

def get_srtm_tile_ids(lonlats):
    """
    Return the set of IDs of SRTM tiles that form a minimal cover of 
    the given longitude-latitude points.

    INPUT:
        - ``lonlats``: list of WGS84 longitude-latitude pairs (float pairs)

    OUTPUT:
        Set of SRTM tile IDs

    NOTES:
        Calls :func:`get_srtm_tile_id`.
    """
    return set(get_srtm_tile_id(lon, lat) for lon, lat in lonlats)

def get_bounds(srtm_tile_id):
    """
    Return the bounding box for the given SRTM tile ID.

    INPUT:
        - ``srtm_tile_id``: string; ID of an SRTM tile

    OUTPUT:
        List of floats of the form  ``[min_lon, min_lat, max_lon, max_lat]``
        representing the WGS84 bounding box of the tile 

    EXAMPLES:

    >>> get_bounds('N04W027')
    [-27, 4, -26, 5]
    """
    t = srtm_tile_id
    min_lat, min_lon = t[:3], t[3:]
    if min_lat[0] == 'N':
        min_lat = float(min_lat[1:])
    else:
        min_lat = -float(min_lat[1:])
    if min_lon[0] == 'E':
        min_lon = float(min_lon[1:])
    else:
        min_lon = -float(min_lon[1:])

    return [min_lon, min_lat, min_lon + 1, min_lat + 1]

def get_polygons(srtm_tile_ids):
    """
    Return a list of (decoded) GeoJSON features, one for each SRTM tile ID 
    in the given list.
    Each feature represents the boundary polygon (rectangle, actually) of 
    the SRTM tile.  
    """
    features = []
    for t in srtm_tile_ids:
        min_lon, min_lat, max_lon, max_lat = get_bounds(t)
        coords = [[min_lon, min_lat], [min_lon, max_lat], 
          [max_lon, max_lat], [max_lon, min_lat], [min_lon, min_lat]]
        features.append({
            'type': 'Feature',
            'properties': {'srtm_tile_id': t},
            'geometry': {
                'type': 'Polygon',
                'coordinates': [coords],
                }
            })
    return features