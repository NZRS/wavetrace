from pathlib import Path 
import re
import csv
import textwrap
import shutil
import subprocess

import wavetrace.utilities as ut


REQUIRED_TRANSMITTER_FIELDS = [
  'network_name',    
  'site_name',
  'latitude', # WGS84 float
  'longitude', # WGS84 float 
  'antenna_height', # meters
  'polarization', # 0 (horizontal) or 1 (vertical)
  'frequency', # mega Herz
  'power_eirp', # Watts
  ]
DIALECTRIC_CONSTANT = 15
CONDUCTIVITY = 0.005
RADIO_CLIMATE = 6
FRACTION_OF_TIME = 0.5

def create_splat_transmitter_data(in_path, out_path):
    """
    INPUTS:

    - ``in_path``: string or Path object; location of a CSV file of transmitter data
    - ``out_path``: string or Path object; directory to which to write outputs

    OUTPUTS:

    None.
    Read the transmitter data given at ``in_path`` and for each transmitter, 
    create the following SPLAT! data for it and save it to the directory
    ``out_path``:

    - location data as a ``.qth`` file
    - irregular terrain model parameter as a ``.lrp`` file
    - azimuth data as a ``.az`` file
    - elevation data as a ``.el`` file

    NOTES:

    The CSV file of transmitter data should include at least the columns

    - ``'network_name'``: name of transmitter network
    - ``'site_name'``: name of transmitter site
    - ``'longitude'``: WGS84 decimal longitude of transmitter  
    - ``'latitude``: WGS84 decimal latitude of transmitter
    - ``'antenna_height'``: height of transmitter antenna in meters above sea level
    - ``'polarization'``: 0 for horizontal or 1 for vertical
    - ``'frequency'``: frequency of transmitter in MegaHerz
    - ``'power_eirp'``: effective radiated power of transmitter in Watts
    """
    ts = read_transmitters(in_path)
    create_splat_qth_data(ts, out_path)
    create_splat_lrp_data(ts, out_path)
    create_splat_az_data(ts, out_path)
    create_splat_el_data(ts, out_path)

def read_transmitters(path):
    """
    INPUTS:

    - ``path``: string or Path object; location of a CSV file of transmitter data

    OUTPUTS:

    Return a list of dictionaries, one for each transmitter in the transmitters
    CSV file.
    The keys for each transmitter come from the header row of the CSV file.
    If ``REQUIRED_TRANSMITTER_FIELDS`` is not a subset of these keys, then
    raise a ``ValueError``
    Additionally, a 'name' field is added to each transmitter dictionary for
    later use and is the result of :func:`build_transmitter_name`.
    """
    path = Path(path)
    transmitters = []
    with path.open() as src:
        reader = csv.DictReader(src)
        header = next(reader) # Skip header
        for row in reader:
            transmitters.append(row)
    transmitters = check_and_format_transmitters(transmitters)
    return transmitters

def check_and_format_transmitters(transmitters):
    """
    INPUTS:

    - ``transmitters``: list; same format as output of :func:`read_transmitters`

    OUTPUTS:

    Return the given list of transmitters dictionaries altered as follows.
    For each dictionary, 

    - create a ``name`` field from the ``network_name`` and ``site_name`` fields
    - convert the numerical fields to floats

    Raise a ``ValueError`` if the list of transmitters is empty, or if the 
    ``REQUIRED_TRANSMITTER_FIELDS`` are not present in each transmitter 
    dictionary, or if the any of the field data is improperly formatted.
    """
    if not transmitters:
        raise ValueError('Transmitters must be a nonempty list')

    # Check that required fields are present
    keys = transmitters[0].keys()
    if not set(REQUIRED_TRANSMITTER_FIELDS) <= set(keys):
        raise ValueError('Transmitters header must contain '\
          'at least the fields {!s}'.format(REQUIRED_TRANSMITTER_FIELDS))

    # Format required fields and raise error if run into problems
    new_transmitters = []
    for i, t in enumerate(transmitters):
        try:
            t['name'] = build_transmitter_name(t['network_name'], 
              t['site_name'])
            for key in ['latitude', 'longitude', 'antenna_height', 
                'polarization', 'frequency', 'power_eirp']:
                t[key] = float(t[key])
        except:
            raise ValueError('Data on line {!s} of transmitters file is '\
              'improperly formatted'.format(i + 1))
        new_transmitters.append(t)

    return new_transmitters

def build_transmitter_name(network_name, site_name):
    """
    INPUTS:

    - ``network_name``: string
    - ``site_name``: string

    OUTPUTS:

    Return a string that is the network name with spaces removed followed 
    by an underscore followed by the site name with spaces removed.
    """
    return network_name.replace(' ', '') + '_' +\
      site_name.replace(' ', '')

def create_splat_qth_data(transmitters, out_path):
    """
    INPUTS:

    - ``transmitters``: list; same form as output of :func:`read_transmitters`
    - ``out_path``: string or Path object specifying a directory

    OUTPUTS:

    For each transmitter in the list of transmitters, create a SPLAT! 
    site location file for the transmitter and save it to the given output 
    directory with the file name ``<transmitter name>.qth``.
    """
    out_path = Path(out_path)
    if not out_path.exists():
        out_path.mkdir(parents=True)
        
    for t in transmitters:
        # Convert to degrees east in range (-360, 0] for SPLAT!
        lon = -t['longitude']
        s = "{!s}\n{!s}\n{!s}\n{!s}m\n".format(
          t['name'], 
          t['latitude'],
          lon, 
          t['antenna_height'])

        path = Path(out_path)/'{!s}.qth'.format(t['name'])
        with path.open('w') as tgt:
            tgt.write(s)

def create_splat_lrp_data(transmitters, out_path, 
  dialectric_constant=DIALECTRIC_CONSTANT, conductivity=CONDUCTIVITY,
  radio_climate=RADIO_CLIMATE, fraction_of_time=FRACTION_OF_TIME):
    """
    INPUTS:

    - ``transmitters``: list; same form as output of :func:`read_transmitters`
    - ``out_path``: string or Path object specifying a directory
    - ``dialectric_constant``: float
    - ``conductivity``: float
    - ``radio_climate``: integer
    - ``fraction_of_time``: float in [0, 1]

    OUTPUTS:

    For each transmitter in the list of transmitters, create a SPLAT! 
    irregular terrain model parameter file for the transmitter 
    and save it to the given output directory with the file name 
    ``<transmitter name>.lrp``.
    """
    out_path = Path(out_path)
    if not out_path.exists():
        out_path.mkdir(parents=True)

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
        {!s} ; ERP in watts
        """.format(
          dialectric_constant, 
          conductivity, 
          t['frequency'],
          radio_climate, 
          t['polarization'], 
          fraction_of_time,
          t['power_eirp'])
        s = textwrap.dedent(s)

        path = Path(out_path)/'{!s}.lrp'.format(t['name'])
        with path.open('w') as tgt:
            tgt.write(s)

def create_splat_az_data(transmitters, out_path):
    """
    INPUTS:

    - ``transmitters``: list; same form as output of :func:`read_transmitters`
    - ``out_path``: string or Path object specifying a directory

    OUTPUTS:

    For each transmitter in the list of transmitters, create a SPLAT! 
    azimuth file for the transmitter and save it to the given output 
    directory with the file name ``<transmitter name>.az``.

    NOTES:

    A transmitter with no ``'bearing'`` or ``'horizontal_beamwidth'`` data will
    produce a file containing the single line ``0  0``.
    """
    out_path = Path(out_path)
    if not out_path.exists():
        out_path.mkdir(parents=True)

    for t in transmitters:
        try:
            bearing = float(t['bearing'])
            hb = float(t['horizontal_beamwidth'])
            left = int(round(360 - (hb/2)))
            right = int(round(hb/2))
            s = '{!s}\n'.format(bearing)
            for x in range(360):
                if left <= x or x <= right:
                    normal = 0.9
                else:
                    normal = 0.1
                s += '{!s}  {!s}\n'.format(x, normal)
        except:
            s = '0  0\n'

        path = Path(out_path)/'{!s}.az'.format(t['name'])
        with path.open('w') as tgt:
            tgt.write(s)

def create_splat_el_data(transmitters, out_path):
    """
    INPUTS:

    - ``transmitters``: list; same form as output of :func:`read_transmitters`
    - ``out_path``: string or Path object specifying a directory

    OUTPUTS:

    For each transmitter in the list of transmitters, create a SPLAT! 
    elevation file for the transmitter and save it to the given output 
    directory with the file name ``<transmitter name>.el``.

    NOTES:

    A transmitter with no ``'bearing'`` or ``'antenna_downtilt'`` or 
    ``'vertical_beamwidth'`` data will produce a file containing the 
    single line ``0  0``.
    """
    out_path = Path(out_path)
    if not out_path.exists():
        out_path.mkdir(parents=True)
        
    for t in transmitters:
        try:
            bearing = float(t['bearing'])
            ad = float(t['antenna_downtilt'])
            vb = float(t['vertical_beamwidth'])
            s = '{!s}  {!s}\n'.format(ad, bearing)
            counter = 0
            for x in range(-10, 91):
                if counter < vb:
                    s += '{!s}  0.9\n'.format(x) 
                else:
                    s += '{!s}  0.1\n'.format(x) 
                counter += 1
        except:
            s = '0  0\n'

        path = Path(out_path)/'{!s}.el'.format(t['name'])
        with path.open('w') as tgt:
            tgt.write(s)

def create_splat_elevation_data(in_path, out_path, high_definition=False):
    """
    INPUTS:

    - ``in_path``: string or Path object specifying a directory
    - ``out_path``: string or Path object specifying a directory
    - ``high_definition``: boolean

    OUTPUTS:

    Converts each SRTM HGT elevation data file in the directory ``in_path`` to
    a SPLAT! Data File (SDF) file in the directory ``out_path``, 
    creating the directory if it does not exist.
    If ``high_definition``, then assume the input data is high definition.

    NOTES:

    - Requires and uses SPLAT!'s ``srtm2sdf`` or ``srtm2sdf-hd`` 
      (if ``high_definition``) command to do the conversion
    - Raises a ``subprocess.CalledProcessError`` if SPLAT! fails to 
      convert a file
    """
    in_path = Path(in_path)
    out_path = Path(out_path)
    if not out_path.exists():
        out_path.mkdir(parents=True)

    splat = 'srtm2sdf'
    if high_definition:
        splat += '-hd'

    sdf_pattern = re.compile(r"[\d\w\-\:]+\.sdf")

    for f in in_path.iterdir():
        if not (f.name.endswith('.hgt') or f.name.endswith('.hgt.zip')):
            continue

        # Unzip if necessary
        is_zip = False
        if f.name.endswith('.zip'):
            is_zip = True
            shutil.unpack_archive(str(f), str(f.parent))
            tile_name = f.name.split('.')[0]
            f = f.parent/'{!s}.hgt'.format(tile_name)

        # Convert to SDF
        cp = subprocess.run([splat, f.name], cwd=str(f.parent),
          stdout=subprocess.PIPE, universal_newlines=True, check=True)

        # Get name of output file, which SPLAT! created and which differs
        # from the original name, and move the output to the out path
        m = sdf_pattern.search(cp.stdout)
        name = m.group(0)        
        src = in_path/name
        tgt = out_path/name
        shutil.move(str(src), str(tgt))

        # Clean up
        if is_zip:
            f.unlink()

@ut.time_it
def create_coverage_reports(in_path, out_path, transmitter_names=None,
  receiver_sensitivity=110, high_definition=False):
    """
    INPUTS:

    - ``in_path``: string or Path object specifying a directory; all the SPLAT! transmitter and elevation data should lie here
    - ``out_path``: string or Path object specifying a directory
    - ``transmitter_names``: list of transmitter names (outputs of :func:`build_transmitter_name`) to restrict to; if ``None``, then all transmitters in ``in_path`` will be used
    - ``receiver_sensitivity``: float; measured in decibels; path loss threshold beyond which signal strength contours will not be plotted
    - ``high_definition``: boolean

    OUTPUTS:

    None. 
    Create a SPLAT! coverage report for every transmitter with data located
    at ``in_path``, or, if ``transmitter_names`` is given, every transmitter 
    in that list with data data located at ``in_path``.
    Write each report to the directory ``out_path``, creating the directory 
    if necessary.
    A report comprises the files

    - ``'<transmitter name>-site_report.txt'``
    - ``'<transmitter name>.kml'``: KML file containing transmitter feature and ``'<transmitter name>.ppm'``
    - ``'<transmitter name>.ppm'``: PPM file depicting a contour plot of the transmitter signal strength
    - ``'<transmitter name>-ck.ppm'``: PPM file depicting a legend for the signal strengths in ``'<transmitter name>.ppm'``

    """
    in_path = Path(in_path)
    out_path = Path(out_path)
    if not out_path.exists():
        out_path.mkdir(parents=True)

    # Get transmitter names
    if transmitter_names is None:
        transmitter_names = [p.stem for p in in_path.iterdir()
          if p.name.endswith('.qth')]

    # Splatify
    splat = 'splat'
    if high_definition:
        splat += '-hd'

    for t in transmitter_names:
        args = [splat, '-t', t + '.qth', '-L', '8.0', '-dbm', '-db', 
          str(receiver_sensitivity), '-metric', '-ngs', '-kml',
          '-o', t + '.ppm']     
        subprocess.run(args, cwd=str(in_path),
          stdout=subprocess.PIPE, universal_newlines=True, check=True)

    # Move outputs to out_path
    exts = ['.ppm', '-ck.ppm', '-site_report.txt', '.kml']
    for t in transmitter_names:
        for ext in exts:
            src = in_path/(t + ext)
            tgt = out_path/(t + ext) 
            shutil.move(str(src), str(tgt))

def postprocess_coverage_reports(path, delete_ppm=True):
    """
    INPUTS:

    - ``path``: string or Path object; directory where coverage reports (outputs of :func:`create_coverage_reports`) lie
    - ``delete_ppm``: boolean; delete the original PPM files in the coverage reports if and only if this flag is ``True``

    OUTPUTS:

    None.
    Convert the PPM files in the directory ``path`` into PNG files,
    and change the PPM reference in each KML file to the corresponding
    PNG file.
    """
    for f in path.iterdir():    
        if f.name.endswith('.ppm'):
            # Convert white background to transparent background
            args = ['convert', '-transparent', '"#FFFFFF"', 
              f.name, f.name]     
            subprocess.run(args, cwd=str(path),
              stdout=subprocess.PIPE, universal_newlines=True, check=True)

            # Resize to width 1200 pixels
            args = ['convert', '-geometry', '1200', f.name, f.name]     
            subprocess.run(args, cwd=str(path),
              stdout=subprocess.PIPE, universal_newlines=True, check=True)

            # Convert to PNG
            args = ['convert', f.name, f.stem + '.png']     
            subprocess.run(args, cwd=str(path),
              stdout=subprocess.PIPE, universal_newlines=True, check=True)

            if delete_ppm:
                # Delete PPM
                f.unlink()

        if f.name.endswith('.kml'):
            # Replace PPM with PNG in KML
            with f.open() as src:
                kml = src.read()

            kml.replace('.ppm', '.png')

            with f.open('w') as tgt:
                tgt.write(kml)        