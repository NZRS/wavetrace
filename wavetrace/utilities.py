"""
CONVENTIONS:
    - All longitudes and latitudes below are referenced to the WGS84 ellipsoid, unless stated otherwise
"""
import os
from functools import wraps
import datetime as dt
import json
from math import ceil, floor
from itertools import product
from pathlib import Path 
import shutil
import re

import requests
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
    Raise a ``ValueError`` if ``lon`` and ``lat`` do not represent a valid 
    longitude-latitude pair.
    Otherwise, return nothing.
    """
    if not (-180 <= lon <= 180):
        raise ValueError('Longitude {!s} is out of bounds'.format(lon))
    if not (-90 <= lat <= 90):
        raise ValueError('Latitude {!s} is out of bounds'.format(lat))

def check_tile_id(tile_id):
    """
    Raise a ``ValueError`` if the given SRTM tile ID (string) 
    is improperly formatted.
    Otherwise, return nothing.
    """
    t = tile_id
    msg = "{!s} is not a valid STRM tile ID".format(t)
    try:
        lat = int(t[1:3])
        lon = int(t[4:])
    except:
        raise ValueError(msg)
    if not(t[0] in ['N', 'S'] and t[3] in ['E', 'W'] and\
      0 <= lat <= 90 and 0 <= lon <= 180):
        raise ValueError(msg)

def get_bounds(tile_id, high_definition=False):
    """
    Return the bounding box for the given SRTM tile ID.

    INPUT:
        - ``tile_id``: string; ID of an SRTM tile

    OUTPUT:
        List of integers of the form  ``[min_lon, min_lat, max_lon, max_lat]``
        representing the longitude-latitude bounding box of the tile 

    EXAMPLES:

    >>> get_bounds('N04W027')
    [-27, 4, -26, 5]
    """
    t = tile_id
    check_tile_id(t)
    min_lat, min_lon = t[:3], t[3:]
    if min_lat[0] == 'N':
        min_lat = int(min_lat[1:])
    else:
        min_lat = -int(min_lat[1:])
    if min_lon[0] == 'E':
        min_lon = int(min_lon[1:])
    else:
        min_lon = -int(min_lon[1:])

    if high_definition:
        # Add 0.5 arcseconds to all four sides
        delta = 0.5/3600
    else:
        # Add 1.5 arcseconds to all four sides
        delta = 1.5/3600

    return [min_lon - delta, min_lat - delta, 
      min_lon + 1 + delta, min_lat + 1 + delta]

def build_polygon(tile_id):
    """
    Given an SRTM tile ID, return a Shapely Polygon object corresponding to the longitude-latitude boundary of the tiles.
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

def extract_tile_id(tile_path):
    """
    Given the path to an SRTM1 or SRTM3 tile, return the ID of the tile (a string), e.g. "S36E174" for the path "bingo/S36E174.SRTMGL1.hgt.zip"
    Assume that the tile ID is the first part of the file name, as is the SRTM convention.
    """
    path = Path(tile_path)
    return path.stem.split('.')[0]

def get_tile_id(lon, lat):
    """
    Return the ID of the SRTM tile that covers the given longitude and latitude. 

    INPUT:
        - ``lon``: float; longitude
        - ``lat``: float; latitude 

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

def compute_intersecting_tiles(geometries, tile_ids=cs.SRTM_NZ_TILE_IDS):
    """
    Given a list of Shapely geometries in WGS84 coordinates, return an ordered list of the unique SRTM tile IDs in ``tile_ids`` whose corresponding tiles intersect the geometries.

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

def get_center(bounds):
    """
    Given a longitude-latitude bounding square, return the longitude-latitude center of the square.
    """
    return (bounds[0] + bounds[2])/2, (bounds[1] + bounds[3])/2

def partition(bounds, n=3):
    """
    Given the bounds of a square with side length ``s``, partition the square into ``n**2`` congruent subsquares, each of side length ``s/n``, and return as a generator of lists the bounds of each of those subsquares, enumerating the squares from left to right and then top to bottom.
    For example, for ``n = 3``, the subsquare order would be::

    -------------
    | 0 | 1 | 2 |
    -------------
    | 3 | 4 | 5 |
    -------------
    | 6 | 7 | 8 |
    -------------
    """
    delta = (bounds[2] - bounds[0])/n
    x0 = bounds[0]
    y0 = bounds[1]
    return ([
      x0 + j*delta, 
      y0 + (n - i - 1)*delta,
      x0 + (j + 1)*delta,
      y0 + (n - i)*delta,
      ] for i in range(n) for j in range(n))

# def get_subtile_bounds(tile_id, n=3):
#     """
#     Given the ID of an SRTM tile, partition the tile into ``n**2`` longitude-latitude squares, each of side length ``1/n`` degrees, and return as a generator of lists the bounds of each of those tiles, enumerating the tiles from west to east and then north to south.
#     For example, for ``n = 3``, the tile order would be::

#     -------------
#     | 0 | 1 | 2 |
#     -------------
#     | 3 | 4 | 5 |
#     -------------
#     | 6 | 7 | 8 |
#     -------------
#     """
#     bounds = get_bounds(tile_id)
#     delta = bounds[2] - bounds[0]
#     x0 = bounds[0]
#     y0 = bounds[1]
#     return ([
#       x0 + j*delta, 
#       y0 + (n - i - 1)*delta,
#       x0 + (j + 1)*delta,
#       y0 + (n - i)*delta,
#       ] for i in range(n) for j in range(n))

def get_geoid_height(lon, lat, num_tries=3):
    """
    Query http://geographiclib.sourceforge.net/cgi-bin/GeoidEval for the height in meters of the EGM96 geoid above the WGS84 ellipsoid for the given longitude and latitude. 
    If the result is negative, then the geoid lies below the ellipsoid.
    Raise a ``ValueError`` if the query fails after ``num_tries`` tries.

    NOTES:
        - It would be good to rewrite this function so that it does not depend on internet access. For a starters, see `https://github.com/vandry/geoidheight <https://github.com/vandry/geoidheight>`_, which uses the EGM2008 ellipsoid.
    """
    url = 'http://geographiclib.sourceforge.net/cgi-bin/GeoidEval'
    data = {'input': '{!s}+{!s}'.format(lat, lon)}
    pattern = r'EGM96</a>\s*=\s*<font color="blue">([\d\.\-]+)</font>'
    
    for i in range(num_tries):
        r = requests.get(url, data)
        if r.status_code != requests.codes.ok:
            continue
            
        m = re.search(pattern, r.text)
        if m is None:
            raise ValueError('Failed to parse data from', url)
        else:
            return float(m.group(1)) 
        
    raise ValueError('Failed to download data from', url)
