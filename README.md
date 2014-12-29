Copyright 2014 .NZ Registry Services

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

# WaveTrace #

This application allows for batch processing of radio propagation modelling.  It takes a CSV as input and generates the following:

1. A KML file with a georeferenced image for sue in the likes of Google Earth.
2. A raster file suitable for use in GIS packages.

The model is derived from a Digital Elevation Model (DEM), the base data at present is from the NASA Shuttle Radio Topography Mission (SRTM).  Thought there may be bettter localised sources available.

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

## Acquiring and Processing DEM Data ##

The get_data.py scrapes the data from NASA.  Some tweaks can be made to limit the area by specifying the latitude and longitude.  At present the default is to acquire New Zealand data only.

get_data.py also processes the data into what can be used in the model.  It unzips and converts to .sdf and cleans up intermediate files.

Usage:
  
  `python get_data.py`
  
## Make Files ##

  `python make_files.py'
  
## Create GIS Outputs ##
`python create_output_from_dir.py'  



