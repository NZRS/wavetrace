import os
from functools import wraps
import datetime as dt
import json
from math import ceil, floor
from itertools import product
from pathlib import Path 
import shutil

from shapely.geometry import box, mapping

import wavetrace.constants as cs


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

def rm_paths(*paths):
    """
    Delete the given file paths/directory paths, if they exists.
    """
    for p in paths:
        p = Path(p)
        if p.exists():
            if p.is_file():
                p.unlink()
            else:
                shutil.rmtree(str(p))

def get_secret(secret, secrets_path=cs.SECRETS_PATH):
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

def get_bounds(tile_id):
    """
    Return the bounding box for the given SRTM tile ID.

    INPUT:
        - ``tile_id``: string; ID of an SRTM tile

    OUTPUT:
        List of integers of the form  ``[min_lon, min_lat, max_lon, max_lat]``
        representing the WGS84 bounding box of the tile 

    EXAMPLES:

    >>> get_bounds('N04W027')
    [-27, 4, -26, 5]
    """
    t = tile_id
    min_lat, min_lon = t[:3], t[3:]
    if min_lat[0] == 'N':
        min_lat = int(min_lat[1:])
    else:
        min_lat = -int(min_lat[1:])
    if min_lon[0] == 'E':
        min_lon = int(min_lon[1:])
    else:
        min_lon = -int(min_lon[1:])

    return [min_lon, min_lat, min_lon + 1, min_lat + 1]

def build_polygon(tile_id):
    """
    Given an SRTM tile ID, return a Shapely Polygon object corresponding to the WGS84 longitude-latitude boundary of the tiles.
    """
    return box(*get_bounds(tile_id))

def build_feature(tile_id):
    """
    Given an SRTM tile ID, a list of (decoded) GeoJSON Feature object corresponding to the WGS84 longitude-latitude boundary of the tile.
    """
    return {
        'type': 'Feature',
        'properties': {'tile_id': tile_id},
        'geometry': mapping(build_polygon(tile_id))
        }

def get_tile_id(lon, lat):
    """
    Return the ID of the SRTM tile that covers the given WGS84 longitude and latitude. 

    INPUT:
        - ``lon``: float; WGS84 longitude
        - ``lat``: float; WGS84 latitude 

    OUTPUT:
        SRTM tile ID (string)
    
    EXAMPLES:

    >>> get_tile_id(27.5, 3.64)
    'N03E027'

    NOTES:
        SRTM data for an output tile might not actually exist, e.g. data for the tile N90E000 does not exist in NASA's database. 
    """
    check_lonlat(lon, lat)

    aflon = abs(floor(lon))
    aflat = abs(floor(lat))
    if lon >= 0:
        prefix = 'E'
    else:
        prefix = 'W'
    lon = prefix + '{:03d}'.format(aflon)

    if lat >= 0:
        prefix = 'N'
    else:
        prefix = 'S'
    lat = prefix + '{:02d}'.format(aflat)

    return lat + lon 

def compute_tile_cover(geometries, tile_ids=cs.SRTM_NZ_TILE_IDS):
    """
    Given a list of Shapely geometries in WGS84 coordinates, return an ordered list of the unique SRTM tile IDs in ``tile_id_set`` whose corresponding tiles intersect the geometries.

    NOTES:
        - Uses a simple double loop instead of a spatial index, so runs in O(num geometries * num tiles) time. That is fast enough for the 65 SRTM tiles that cover New Zealand. Could be fast enough for all SRTM tiles, but i never tried. 
    """
    result = []
    for tid in set(tile_ids):
        poly = build_polygon(tid)
        for geom in geometries:
            if poly.intersects(geom):
                result.append(tid)
                break
    return sorted(result)
