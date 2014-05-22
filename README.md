Copyright 2014 .NZ Registry Services

This software is licensed under the GPLv3 license.

# WaveTrace #

This application allows for batch processing of radio propagation modelling.  It takes a CSV as input and generates the following:

1. A KML file with a georeferenced image for sue in the likes of Google Earth.
2. A raster file suitable for use in GIS packages.

The model is derived from a Digital Elevation Model (DEM), the base data at present is from the NASA Shuttle Radio Topography Mission (SRTM).  Thought there may be bettter localised sources available.

## Acquiring and Processing DEM Data ##

The get_data.py scrapes the data from NASA.  Some tweaks can be made to limit the area by specifying the latitude and longitude.  At present the default is to acquire New Zealand data only.

get_data.py also processes the data into what can be used in the model.  It unzips and converts to .sdf and cleans up intermediate files.

Usage:
  
  python get_data.py
  




