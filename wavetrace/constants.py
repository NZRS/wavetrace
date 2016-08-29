import os
from pathlib import Path


PROJECT_ROOT = Path(os.path.abspath(os.path.join(
  os.path.dirname(__file__), '../')))
SECRETS_PATH = PROJECT_ROOT/'secrets.json'

#: SRTM tiles that cover New Zealand; for a visual, see http://geojson.io/#id=gist:anonymous/81b4cb465f1c78941f665c9038494f0f&map=5/-41.360/172.463
SRTM_NZ_TILE_IDS = [
  'S35E172',
  'S35E173',
  'S36E173',
  'S36E174',
  'S36E175',
  'S37E173',
  'S37E174',
  'S37E175',
  'S37E176',
  'S38E174',
  'S38E175',
  'S38E176',
  'S38E177',
  'S38E178',
  'S39E174',
  'S39E175',
  'S39E176',
  'S39E177',
  'S39E178',
  'S40E173',
  'S40E174',
  'S40E175',
  'S40E176',
  'S40E177',
  'S40E178',
  'S41E172',
  'S41E173',
  'S41E174',
  'S41E175',
  'S41E176',
  'S42E171',
  'S42E172',
  'S42E173',
  'S42E174',
  'S42E175',
  'S42E176',
  'S43E170',
  'S43E171',
  'S43E172',
  'S43E173',
  'S43E174',
  'S44E168',
  'S44E169',
  'S44E170',
  'S44E171',
  'S44E172',
  'S44E173',
  'S45E167',
  'S45E168',
  'S45E169',
  'S45E170',
  'S45E171',
  'S46E166',
  'S46E167',
  'S46E168',
  'S46E169',
  'S46E170',
  'S46E171',
  'S47E166',
  'S47E167',
  'S47E168',
  'S47E169',
  'S47E170',
  'S48E167',
  'S48E168',
  ]

#: Transmitter CSV files must have these header columns
REQUIRED_TRANSMITTER_FIELDS = [
  'network_name',    
  'site_name',
  'latitude', # WGS84 float
  'longitude', # WGS84 float 
  'antenna_height', # meters
  'polarization', # 0 (horizontal) or 1 (vertical)
  'frequency', # megaherz
  'power_eirp', # watts
  ]

#: SPLAT! Earth dielectric constant.
#: According to the SPLAT! documentation, typical Earth dielectric constants and conductivities are: 
#: Salt water, 80, 5.000;
#: Good ground, 25, 0.020;
#: Fresh water, 80, 0.010;
#: Marshy land, 12, 0.007;
#: Farmland or forest, 15, 0.005;
#: Average ground, 15, 0.005;
#: Mountain or sand, 13, 0.002;
#: City, 5, 0.001;
#: Poor ground, 4, 0.001;
EARTH_DIELECTRIC_CONSTANT = 15

#: SPLAT! Earth earth_conductivity in Siemens per meter
EARTH_CONDUCTIVITY = 0.005

#: SPLAT! radio climate codes.
#: 1=Equatorial (Congo);
#: 2=Continental Subtropical (Sudan);
#: 3=Maritime Subtropical (West coast of Africa);
#: 4=Desert (Sahara);
#: 5=Continental Temperate;
#: 6=Maritime Temperate, over land (UK and west coasts of US & EU);
#: 7=Maritime Temperate, over sea
RADIO_CLIMATE = 6

#: SPLAT! time variability parameter
FRACTION_OF_TIME = 0.5

#: SPLAT! location variability parameter
FRACTION_OF_SITUATIONS = 0.5

#: SPLAT receiver sensitivity parameter in decibel-milliwatts (dBm). 
#: For example, minimum received signal power of wireless networks (802.11 variants) is -100 dBm.
RECEIVER_SENSITIVITY = -110 
#: WGS84 semimajor axis in meters
WGS84_A = 6378137
#: WGS84 flattening 
WGS84_F = 1/298.257223563
#: WGS84 eccentricity squared (e^2)
WGS84_E2 = 2*WGS84_F - WGS84_F**2
#: Distance in meters of a geostationary satellite from the center of the Earth (and hence the center of the WGS84 ellipsoid);
#: taken from the Wikipedia article `Geostationary orbit <https://en.wikipedia.org/wiki/Geostationary_orbit>`_
R_S = 42164000
#: Distance in meters of a geostationary satellite from the WGS84 ellipsoid
H_S = R_S - WGS84_A