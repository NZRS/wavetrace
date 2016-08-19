import os
from pathlib import Path


PROJECT_ROOT = Path(os.path.abspath(os.path.join(
  os.path.dirname(__file__), '../')))
SECRETS_PATH = PROJECT_ROOT/'secrets.json'
#: SRTM tiles covering New Zealand
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
#:
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
#:
DIELECTRIC_CONSTANT = 15
#:
CONDUCTIVITY = 0.005
#:
RADIO_CLIMATE = 6
#:
FRACTION_OF_TIME = 0.5
#:
RECEIVER_SENSITIVITY = -110 # decibels