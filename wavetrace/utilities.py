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
import subprocess
import math

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

def get_bounds(tile_id, be_precise=None):
    """
    Return the bounding box for the given SRTM tile ID.

    INPUT:
        - ``tile_id``: string; ID of an SRTM tile
        - ``be_precise`` (optional): string; 'SRTM1' or 'SRTM3' 

    OUTPUT:
        List of integers of the form  ``[min_lon, min_lat, max_lon, max_lat]``
        representing the longitude-latitude bounding box of the tile.
        This assumes that the tile is exactly 1 degree by 1 degree in dimension, which is not actually the case. 
        If ``be_precise`` equals 'SRTM1' or 'SRTM3', then return the precise bounds corresponding to the tile type; SRTM1 tiles are 1 degree and 1 arcsecond in side length; SRTM3 tiles are 1 degree and 3 arcseconds in side length.   

    EXAMPLES:

    >>> get_bounds('N04W027')
    [-27, 4, -26, 5]
    >>> get_bounds('N04W027', be_precise='SRTM1')
    [-27.000138888888888, 3.999861111111111, -25.999861111111112, 5.0001388888888885]
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

    if be_precise == 'SRTM1':
        # Add 0.5 arcseconds to all four sides
        delta = 0.5/3600
    elif be_precise == 'SRTM3':
        # Add 1.5 arcseconds to all four sides
        delta = 1.5/3600
    else:
        delta = 0

    return [min_lon - delta, min_lat - delta, 
      min_lon + 1 + delta, min_lat + 1 + delta]

def build_polygon(tile_id, be_precise=None):
    """
    Given an SRTM tile ID, return a Shapely Polygon object corresponding to the longitude-latitude boundary of the tiles.
    Use the same ``be_precise`` keyword as in :func:`get_bounds`.
    """
    return box(*get_bounds(tile_id, be_precise))

def build_feature(tile_id, be_precise=None):
    """
    Given an SRTM tile ID, a list of (decoded) GeoJSON Feature object corresponding to the WGS84 longitude-latitude boundary of the tile.
    Use the same ``be_precise`` keyword as in :func:`get_bounds`.
    """
    return {
        'type': 'Feature',
        'properties': {'tile_id': tile_id},
        'geometry': mapping(build_polygon(tile_id, be_precise))
        }

def get_tile_id(tile_path):
    """
    Given the path to an SRTM1 or SRTM3 tile, return the ID of the tile (a string), e.g. "S36E174" for the path "bingo/S36E174.SRTMGL1.hgt.zip"
    Assume that the tile ID is the first part of the file name, as is the SRTM convention.
    """
    path = Path(tile_path)
    return path.stem.split('.')[0]

def get_covering_tile_id(lon, lat):
    """
    Return the ID of the SRTM tile that covers the given longitude and latitude. 

    INPUT:
        - ``lon``: float; longitude
        - ``lat``: float; latitude 

    OUTPUT:
        SRTM tile ID (string)
    
    EXAMPLES:

    >>> get_covering_tile_id(27.5, 3.64)
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

def gdalinfo(path):
    """
    Given the path to an raster file, run ``gdalinfo`` on the file and extract and return from the result a dictionary with the following keys and values:

    - ``'width'``: pixel width of raster
    - ``'height'``: pixel height of raster
    - ``'center'``: center coordinates.
    """
    path = Path(path)
    args = ['gdalinfo', str(path)]
    sp = subprocess.run(args, 
      stdout=subprocess.PIPE, universal_newlines=True, check=True)
    text = sp.stdout
    m = re.search(r'Size is (\d+), (\d+)', text)
    width, height = map(int, m.group(1, 2))
    m = re.search(r'Center\s*\(\s*([\d\.\-]+),\s*([\d\.\-]+)\s*\)', text)
    center0, center1 = map(float, m.group(1, 2))
    return {
        'width': width, 
        'height': height,
        'center': (center0, center1),
        }    