Copyright 2014-2015 NZRS Ltd

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

# WaveTrace #

This application allows for batch processing of radio propagation modelling.  It takes a CSV as input and generates the following:

1. A KML file with a georeferenced image for use in the likes of Google Earth.
2. A raster file suitable for use in GIS packages.

The model is derived from a Digital Elevation Model (DEM), the base data at present is from the NASA Shuttle Radio Topography Mission (SRTM).  Though there may be bettter localised sources available.

## Set Up ##

Install the following packages [setup.md](https://github.com/NZRegistryServices/wavetrace/blob/master/setup.md)

## Parameters Used in Modelling Coverage ##

* network_name	
* site_name	
* latitude	
* longitude	
* antenna height	
* frequency (MHz)	
* power (EIRP)	
* polarisation	
* bearing	
* horizontal beamwidth	
* vertical beamwidth	
* antenna downtilt

The [Longely Rice Prediction Model](http://en.wikipedia.org/wiki/Longley%E2%80%93Rice_model "Link to Wikipedia") is used to model coverage.

## The Process of Creating Coverage - Short Version##

1. Get the Digital Elevation Model Files and convert of .sdf 
  * Either get from NASA using get_data.py which scrapes and converts to .sdf files, or;
  * Copy already processed .sdf files from a local source
  * Or download from NZRS (once we have a site up)
2. Ensure you have a .csv file that matches the column headings of  sample_data.csv in this repository.  The file must contain the following:
  * network_name	
  * site_name	latitude	
  * longitude	
  * antenna_height	
  * frequency_mhz	
  * power_eirp
  
  It may optionally contain

  * polarisation	
  * bearing	
  * horizontal_beamwidth	
  * vertical_beamwidth
3. Use make_files.py to create the model files based off of the .csv file.
  * Azimuth file
  * Elevation file 
  * QTH file
  * LRP file
4. Map coverage using create_output_from_dir.py.  The following will be created:
  * A KML file you can use in Google Earth
  * A georeferenced .tif file (raster - 1 file)
  * A shapefile (vector - 4 files)

## The Process of Creating Converage - Long Version##

## Acquiring and Processing DEM Data ##

The get_data.py scrapes the data from NASA.  Some tweaks can be made to limit the area by specifying the latitude and longitude.  At present the default is to acquire New Zealand data only.  Though the query_url in 'get_data.py' can be modified easily.

get_data.py also processes the data into what can be used in the model.  It unzips and converts to .sdf and cleans up intermediate files.

### Usage: ###
  
  `python get_data.py`
  
get_data.py does the following:

* Scrapes the Shuttle Radar Topography Mission (SRTM) data from NASA
* Unzips the downloaded data
* Converts the downloaded .hgt files to .sdf files
* Cleans stuff up

  
## Creating Files For the Model ##
The model uses four files, two required and two optional but created empty by default.
Required files:
* LRP - Contains Longley Rice Parameters. Where not read from the .csv file they default to New Zealand specific parameters, they may need changed for other climates and locales.
  * Earth Dielectric Constant (Relative permittivity)
  * Earth Conductivity (Siemens per meter)
  * Atmospheric Bending Constant (N-units)
  * Frequency in MHz (20 MHz to 20 GHz)
  * Climate type (Maritime Temperate, over land)
  * Polarization (0 = Horizontal, 1 = Vertical)
  * Fraction of situations (50% of locations)
  * Fraction of time (50% of the time)
  * Power EIRP
* QTH - Geographic
  * Latitude
  * Longitude
  * Antenna height above ground
* AZ - Azimuth
  * Bearing
  * Horizontal beamwidth
* EL - Elevation
  * Downtilt
  * Vertical beamwidth

The AZ and EL files use a simplified model where 90% of the energy is transmitted in the specified beamwidth and the other 10% outside of the beamwidth.  Both files can hold full antenna patterns but this has been simplified for bathc modelling.

### Usage ###

  `python wavetrace/python make_files.py'
  
## Create GIS Outputs ##
`python create_output_from_dir.py'  

## Mapping coverage ##
This requires all the following files to be in the same directory:
 * The .sdf files
 * LRP files
 * QTH files
 * EZ files
 * EL files

The above files will be processed when create_ouput_from_dir.py is run.  The default system receive is modelled by default at -110 dBm receive.  Other receives can be passed in as a parameter.   Note this is at the chip, so includes receive antenna gain.

You may need to change received values to get something that feels right.

### Usage ###
`python create_output_from_dir.py`

or for say -105dBm receive

`python create_output_from_dir.py -105`




