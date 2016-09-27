import click

import wavetrace.constants as cs 
import wavetrace.utilities as ut 
import wavetrace.main as m


@click.group()
def wavey(**kwargs):
    pass

@wavey.command(short_help="Process transmitter data (CSV)")
@click.argument('in_path', type=click.Path())
@click.argument('out_path', type=click.Path())
@click.option('-edc', '--earth_dielectric_constant', type=float, 
  default=cs.EARTH_DIELECTRIC_CONSTANT,
  help="SPLAT! Earth dielectric constant (relative permittivity)")
@click.option('-ec', '--earth_conductivity', type=float, 
  default=cs.EARTH_CONDUCTIVITY,
  help="SPLAT! Earth earth_conductivity (Siemens per meter)")
@click.option('-rc', '--radio_climate', type=click.IntRange(1, 7), 
  default=cs.RADIO_CLIMATE,  
  help="SPLAT! radio climate code; 1=Equatorial (Congo), 2=Continental Subtropical (Sudan), 3=Maritime Subtropical (West coast of Africa), 4=Desert (Sahara), 5=Continental Temperate, 6=Maritime Temperate, over land (UK and west coasts of US & EU), 7=Maritime Temperate, over sea")
@click.option('-ft', '--fraction_of_time', type=float,
  default=cs.FRACTION_OF_TIME,
  help="SPLAT! time variability")
@click.option('-fs', '--fraction_of_situations', type=float,
  default=cs.FRACTION_OF_SITUATIONS,
  help="SPLAT! location variability")
def process_transmitters(in_path, out_path, 
  earth_dielectric_constant, earth_conductivity, radio_climate, 
  fraction_of_time, fraction_of_situations):
    """
    Read a CSV file of transmitter data located at IN_PATH, and for each transmitter, create its following SPLAT! files and save them to the directory OUT_PATH.

    \b
    - QTH file; location data
    - LRP file; irregular topography model parameter data
    - AZ file; azimuth data
    - EL file; elevation data

    The CSV file of transmitter data should include at least the following columns, otherwise a ValueError will be raised.

    \b
    - network_name: name of transmitter network
    - site_name: name of transmitter site
    - longitude: WGS84 decimal longitude of transmitter  
    - latitude: WGS84 decimal latitude of transmitter
    - antenna_height: height of transmitter antenna in meters above sea level
    - polarization: 0 for horizontal or 1 for vertical
    - frequency: frequency of transmitter in MegaHerz
    - power_eirp: effective radiated power of transmitter in Watts
    """
    m.process_transmitters(in_path=in_path, out_path=out_path,
      earth_dielectric_constant=earth_dielectric_constant, 
      earth_conductivity=earth_dielectric_constant, 
      radio_climate=radio_climate, 
      fraction_of_time=fraction_of_time,
      fraction_of_situations=fraction_of_situations)

@wavey.command(short_help="List the SRTM tiles that cover New Zealand")
def srtm_nz():
    """
    List the IDs of the SRTM tiles that cover New Zealand (SRTM NZ tiles)
    """
    click.echo(' '.join(cs.SRTM_NZ_TILE_IDS))

@wavey.command(short_help="Compute SRTM tiles IDs needed")
@click.argument('path', type=click.Path())
@click.option('-b', '--transmitter_buffer', type=float, default=0.5,
  help="Distance in decimal degrees with which to buffer each transmitter when computing a tile cover")
def get_covering_tiles_ids(path, transmitter_buffer):
    """
    Read the CSV of transmitter data located at PATH, get the location of each transmitter, buffer each location by ``transmitter_buffer`` decimal degrees, and return an ordered list of unique New Zealand SRTM tile IDs whose corresponding tiles intersect the buffers.
    
    As long as TRANSMITTER_BUFFER is big enough, which the default setting is, the result will be a list of tile IDs to use when computing coverage for the given transmitters.
    
    By the way, one degree of latitude represents about 111 km on the ground and one degree of longitude at -45 degrees latitude represents about 78 km on the ground; see https://en.wikipedia.org/wiki/Decimal_degrees
    """
    tms = m.read_transmitters(path)
    tids = m.get_covering_tiles_ids(tms, transmitter_buffer=transmitter_buffer)
    click.echo(' '.join(tids))

@wavey.command(short_help="Download topography data (SRTM)")
@click.argument('tile_ids', nargs=-1)
@click.argument('path', type=click.Path())
@click.argument('api_key')
@click.option('-hd/-sd', '--high-definition/--standard-definition', 
  default=False,
  help="If True, then download SRTM1 tiles; otherwise download SRTM3 tiles")
def download_topography(tile_ids, path, api_key, high_definition):
    """
    Download from the Gitlab repository https://gitlab.com/araichev/srtm_nz the SRTM1 (high definition) or SRTM3 (standard definition) topography data corresponding to the given SRTM tile IDs and save the files to the directory PATH, creating the directory if it does not exist.
    This requires a Gitlab API key (access token).

    This command only works for SRTM tiles covering New Zealand ---use :func:`srtm_nz` to list these--- and raises a ``ValueError`` if other tiles are given.
    """
    m.download_topography(tile_ids, path, api_key, high_definition)

@wavey.command(short_help="Process topography data (SRTM)")
@click.argument('in_path', type=click.Path())
@click.argument('out_path', type=click.Path())
@click.option('-hd/-sd', '--high-definition/--standard-definition', 
  default=False,
  help="If True, then assume topography data is high definition (SRTM1); otherwise assume it is standard definition (SRTM3)")
def process_topography(in_path, out_path, high_definition):
    """
    Convert each SRTM HGT topography file in the directory IN_PATH to
    a SPLAT! Data File (SDF) file in the directory OUT_PATH, 
    creating the directory if it does not exist.

    This command calls SPLAT!'s ``srtm2sdf`` or ``srtm2sdf-hd`` (if ``high_definition``) command to do the work
    """
    m.process_topography(in_path, out_path, high_definition)

@wavey.command(short_help="Compute radio signal coverage reports")
@click.argument('in_path', type=click.Path())
@click.argument('out_path', type=click.Path())
@click.option('-rs', '--receiver_sensitivity', type=float, 
  default=cs.RECEIVER_SENSITIVITY)
@click.option('-hd/-sd', '--high-definition/--standard-definition', 
  default=False,
  help="If True, then assume source topography data is high definition (SRTM1); otherwise assume it is standard definition (SRTM3)")
def compute_coverage(in_path, out_path, receiver_sensitivity, high_definition):
    """
    Create and post-process a SPLAT! coverage report for every transmitter with data located at IN_PATH.
    Write each report to the directory OUT_PATH, creating the directory if necessary.
    Each resulting report comprises the files

    \b
    - <transmitter name>-site_report.txt
    - <transmitter name>.kml: KML file containing transmitter feature and ``'<transmitter name>.png'``
    - <transmitter name>.png: PNG file depicting a contour plot of the transmitter signal strength
    - <transmitter name>.tif: GeoTIFF file depicting a contour plot of the transmitter signal strength
    - <transmitter name>-ck.png: PNG file depicting a legend for the signal strengths in ``'<transmitter name>.tif'``

    This command calls SPLAT!'s ``splat`` or ``splat-hd`` (if ``high_definition``) command to do the work

    This is a time-intensive command. On a 3.6 GHz Intel Core i7 processor with 16 GB of RAM, this takes about 32 minutes for the 20 New Zealand test transmitters with their 13 standard definition topography files and takes about 687 minutes for the same 20 transmitters with their 13 high definition topography files.
    """
    m.compute_coverage(in_path, out_path, 
      receiver_sensitivity=receiver_sensitivity, 
      high_definition=high_definition, keep_ppm=False)

@wavey.command(short_help="Compute satellite line-of-sight")
@click.argument('in_path', type=click.Path())
@click.argument('satellite_lon', type=click.FLOAT)
@click.argument('out_path', type=click.Path())
@click.option('-n', type=click.INT, default=3, help="The given SRTM tile is partitioned into n**2 subtiles of roughly the same size and then satellite line-of-sights are computed for each subtile")
def compute_satellite_los(in_path, satellite_lon, out_path, n):
    """
    Given the path to an SRTM1 or SRTM3 file and the longitude SATELLITE_LON of a geostationary satellite, color with 8-bits of grayscale the raster cells according to whether they are in (whitish) or out (blackish) of the line-of-site of the satellite, and save the result as a GeoTIFF file located at OUT_PATH.

    \b
    ALGORITHM: 
        1. Partition the SRTM tile into n**2 square subtiles or roughly the same size
        2. For each subtile, compute the longitude, latitude, and (WGS84) height of its center 
        3. Compute the the look angles of the satellite from the center 
        4. Use the look angles to shade the subtile via GDAL's ``gdaldem hillshade`` command
        5. Merge the subtiles and save the result as a GeoTIFF file

    \b
    NOTES:
        - This function depends on a webservice for computing geoid heights, so requires internet access 
    """
    m.compute_satellite_los(in_path, satellite_lon, out_path, n)