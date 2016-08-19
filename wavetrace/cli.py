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
@click.option('-dc', '--dielectric_constant', type=float, 
  default=cs.DIELECTRIC_CONSTANT,
  help="Earth dielectric constant (relative permittivity)")
@click.option('-c', '--conductivity', type=float, 
  default=cs.CONDUCTIVITY,
  help="Earth conductivity (Siemens per meter)")
@click.option('-rc', '--radio_climate', type=click.IntRange(1, 7), 
  default=cs.RADIO_CLIMATE,  
  help="radio climate; 1=Equatorial (Congo), 2=Continental Subtropical (Sudan), 3=Maritime Subtropical (West coast of Africa), 4=Desert (Sahara), 5=Continental Temperate, 6=Maritime Temperate, over land (UK and west coasts of US & EU), 7=Maritime Temperate, over sea")
@click.option('-ft', '--fraction_of_time', type=float,
  default=cs.FRACTION_OF_TIME,
  help="transmitter time variability")
def process_transmitters(in_path, out_path, dielectric_constant, conductivity,
  radio_climate, fraction_of_time):
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
    m.create_splat_transmitter_files(in_path=in_path, out_path=out_path,
      dielectric_constant=dielectric_constant, 
      conductivity=dielectric_constant, radio_climate=radio_climate, 
      fraction_of_time=fraction_of_time)

@wio.command()
def srtm_nz():
    """
    List the IDs of the SRTM tiles that cover New Zealand (SRTM NZ tiles)
    """
    click.echo(' '.join(cs.SRTM_NZ_TILE_IDS))

@wio.command()
@click.argument('path', type=click.Path())
@click.option('-b', '--transmitter_buffer', type=float, default=0.5,
  help="distance in decimal degrees with which to buffer each transmitter when computing a tile cover")
def compute_tile_ids(path, transmitter_buffer):
    """
    Read the CSV of transmitter data located at PATH, get the location of each transmitter, buffer each location by ``transmitter_buffer`` decimal degrees, and return an ordered list of unique New Zealand SRTM tile IDs whose corresponding tiles intersect the buffers.
    
    As long as ``transmitter_buffer`` is big enough, which the default setting is, the result will be a list of tile IDs to use when computing coverage for the given transmitters.
    
    By the way, one degree of latitude represents about 111 km on the ground and one degree of longitude at -45 degrees latitude represents about 78 km on the ground; see https://en.wikipedia.org/wiki/Decimal_degrees
    """
    tms = m.read_transmitters(path)
    tids = m.compute_tile_ids(tms, transmitter_buffer=transmitter_buffer)
    click.echo(' '.join(tids))

@wio.command()
@click.argument('tile_ids', nargs=-1)
@click.argument('path', type=click.Path())
@click.argument('api_key')
@click.option('-hd/-sd', '--high-definition/--standard-definition', 
  default=False,
  help="if True, then download SRTM1 tiles; otherwise download SRTM3 tiles")
def download_topography(tile_ids, path, api_key, high_definition):
    """
    Download from the Gitlab repository https://gitlab.com/araichev/srtm_nz the SRTM1 (high definition) or SRTM3 (standard definition) topography data corresponding to the given SRTM tile IDs and save the files to the directory PATH, creating the directory if it does not exist.
    This requires a Gitlab API key (access token).

    This command only works for SRTM tiles covering New Zealand ---use :func:`srtm_nz` to list these--- and raises a ``ValueError`` if other tiles are given.
    """
    m.download_srtm(tile_ids, path, api_key, high_definition)

@wio.command()
@click.argument('in_path', type=click.Path())
@click.argument('out_path', type=click.Path())
@click.option('-hd/-sd', '--high-definition/--standard-definition', 
  default=False,
  help="if True, then assume topography data is high definition (SRTM1); otherwise assume it is standard definition (SRTM3)")
def process_topography(in_path, out_path, high_definition):
    """
    Convert each SRTM HGT topography file in the directory IN_PATH to
    a SPLAT! Data File (SDF) file in the directory OUT_PATH, 
    creating the directory if it does not exist.

    This command calls SPLAT!'s ``srtm2sdf`` or ``srtm2sdf-hd`` (if ``high_definition``) command to do the work
    """
    m.create_splat_topography_files(in_path, out_path, high_definition)

@wio.command()
@click.argument('in_path', type=click.Path())
@click.argument('out_path', type=click.Path())
@click.option('-rs', '--receiver_sensitivity', type=float, 
  default=cs.RECEIVER_SENSITIVITY)
@click.option('-hd/-sd', '--high-definition/--standard-definition', 
  default=False,
  help="if True, then assume source topography data is high definition (SRTM1); otherwise assume it is standard definition (SRTM3)")
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
      high_definition=high_definition)
    m.postprocess_coverage(out_path, keep_ppm=False)