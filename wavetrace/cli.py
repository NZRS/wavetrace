import click

import wavetrace.constants as cs 
import wavetrace.utilities as ut 
import wavetrace.main as m



@click.group()
def wio(**kwargs):
    pass

@wio.command()
@click.argument('in_path', type=click.Path())
@click.argument('out_path', type=click.Path())
@click.argument('-dc', '--dialectric_constant', default=cs.DIALECTRIC_CONSTANT)
@click.option('-c', '--conductivity', default=cs.CONDUCTIVITY)
@click.option('-rc', '--radio_climate', default=cs.RADIO_CLIMATE)
@click.option('-ft', '--fraction_of_time', default=cs.FRACTION_OF_TIME)
def process_transmitters(in_path, out_path, dialectric_constant, conductivity,
  radio_climate, fraction_of_time):
    """
    Read the CSV transmitter data at ``in_path``, and for each transmitter, 
    create the following SPLAT! data for it and save it to the directory
    ``out_path``:

    - location data as a ``.qth`` file
    - irregular topography model parameter as a ``.lrp`` file
    - azimuth data as a ``.az`` file
    - elevation data as a ``.el`` file

    INPUT:
        - ``in_path``: string or Path object; location of a CSV file of transmitter data
        - ``out_path``: string or Path object; directory to which to write outputs
        - ``dialectric_constant``: float; used to make SPLAT! ``.lrp`` file
        - ``conductivity``: float; used to make SPLAT! ``.lrp`` file
        - ``radio_climate``: integer; used to make SPLAT! ``.lrp`` file
        - ``fraction_of_time``: float in [0, 1]; used to make SPLAT! ``.lrp`` file

    OUTPUT:
        None.

    NOTES:
        The CSV file of transmitter data should include at least the columns,
        otherwise a ``ValueError`` will be raised.

        - ``'network_name'``: name of transmitter network
        - ``'site_name'``: name of transmitter site
        - ``'longitude'``: WGS84 decimal longitude of transmitter  
        - ``'latitude``: WGS84 decimal latitude of transmitter
        - ``'antenna_height'``: height of transmitter antenna in meters above sea level
        - ``'polarization'``: 0 for horizontal or 1 for vertical
        - ``'frequency'``: frequency of transmitter in MegaHerz
        - ``'power_eirp'``: effective radiated power of transmitter in Watts
    """
    m.create_splat_transmitter_files(in_path=in_path, out_path=out_path,
      dialectric_constant=dialectric_constant, 
      conductivity=dialectric_constant, radio_climate=radio_climate, 
      fraction_of_time=fraction_of_time)

@wio.command()
def srtm_nz():
    """
    List the IDs of the SRTM tiles that cover New Zealand.
    """
    click.echo(cs.SRTM_NZ_TILE_IDS)

@wio.command()
def download_topography(out_path, api_key, tile_ids=None, 
  transmitters_path=None, transmitter_buffer=0.5, high_definition=False):
    """
    Download from the Gitlab repository https://gitlab.com/araichev/srtm_nz the SRTM1 or SRTM3 topography data corresponding to the given SRTM tile IDs and save the files to the directory ``path``, creating the directory if it does not exist.
    Alternatively, download the tiles that intersect the buffered locations of the transmitters listed in the CSV file at ``transmitters_path``

    INPUT:
        - ``tile_ids``: list of strings; SRTM tile IDs
        - ``out_path``: string or Path object specifying a directory
        - ``api_key``: string; a valid Gitlab API key (access token)
        - ``transmitters_path``: string or Path object specifying a transmitters CSV file
        - ``transmitter_buffer``: float; distance in decimal degrees with which to buffer each transmitter to search for intersecting SRTM tiles; for reference, one degree of latitude represents about 111 km and one degree of longitude at -45 degrees latitude represents about 78 km (see https://en.wikipedia.org/wiki/Decimal_degrees) 
        - ``high_definition``: boolean; if ``True`` then download SRTM1 tiles; otherwise download SRTM3 tiles

    OUTPUT:
        None

    NOTES:
        Only works for SRTM tiles covering New Zealand ---use :func:`srtm_nz` to list these--- and raises a ``ValueError`` if other tiles are given.
    """
    if tile_ids is None and transmitters_path is None:
        raise ValueError('At least one of tile_ids or transmitters_path '\
          'must not be None')

    # Compute tiles from transmitters if appropriate
    if transmitters_path is not None:
        ts = m.read_transmitters(transmitters_path)
        blobs = [Point(p).buffer(transmitter_buffer) 
          for p in m.get_lonlats(ts)]
        tile_ids = ut.compute_tile_cover(blobs)

    m.download_srtm(tile_ids, out_path, api_key, high_definition)

@wio.command()
def process_topography(in_path, out_path, high_definition=False):
    """
    Convert each SRTM HGT topography file in the directory ``in_path`` to
    a SPLAT! Data File (SDF) file in the directory ``out_path``, 
    creating the directory if it does not exist.
    If ``high_definition``, then assume the input data is high definition.

    INPUT:
        - ``in_path``: string or Path object specifying a directory
        - ``out_path``: string or Path object specifying a directory
        - ``high_definition``: boolean

    OUTPUT:
        None.

    NOTES:
        - Calls SPLAT!'s ``srtm2sdf`` or ``srtm2sdf-hd`` 
          (if ``high_definition``) command to do the work
        - Raises a ``subprocess.CalledProcessError`` if SPLAT! fails to 
          convert a file
    """
    m.create_splat_topography_files(in_path, out_path, high_definition)

@wio.command()
def compute_coverage(in_path, out_path, 
  receiver_sensitivity=cs.RECEIVER_SENSITIVITY, high_definition=False):
    """
    Create and postprocess a SPLAT! coverage report for every transmitter with data located at ``in_path``.
    Write each report to the directory ``out_path``, creating the directory if necessary.
    Each resulting report comprises the files

    - ``'<transmitter name>-site_report.txt'``
    - ``'<transmitter name>.kml'``: KML file containing transmitter feature and ``'<transmitter name>.png'``
    - ``'<transmitter name>.png'``: PNG file depicting a contour plot of the transmitter signal strength
    - ``'<transmitter name>.tif'``: GeoTIFF file depicting a contour plot of the transmitter signal strength
    - ``'<transmitter name>-ck.png'``: PNG file depicting a legend for the signal strengths in ``'<transmitter name>.tif'``

    INPUT:
        - ``in_path``: string or Path object specifying a directory; all the SPLAT! transmitter and elevation data should lie here
        - ``out_path``: string or Path object specifying a directory
        - ``receiver_sensitivity``: float; measured in decibels; path loss threshold beyond which signal strength contours will not be plotted
        - ``high_definition``: boolean; set to ``True`` if using high definition (SRTM1) topography data

    OUTPUT:
        None. 

    NOTES:
        - Calls SPLAT!'s ``splat`` or ``splat-hd`` (if ``high_definition``) command to do the work
        - Raises a ``subprocess.CalledProcessError`` if SPLAT! fails
        - This is a time-intensive function. On a 3.6 GHz Intel Core i7 processor with 16 GB of RAM, this takes about 32 minutes for the 20 New Zealand test transmitters (in ``tests/data/transmitters.csv``) with their 13 standard definition topography files and takes about 687 minutes for the same 20 transmitters with their 13 high definition topography files.
    """
    m.compute_coverage(in_path, out_path, 
      receiver_sensitivity=receiver_sensitivity, 
      high_definition=high_definition)
    m.postprocess_coverage(out_path, keep_ppm=False)