Workflows
***********

Workflows for producing coverage reports around New Zealand.


Workflow 1
===========

Create coverage reports using SRTM3 tiles which provide a resolution of roughly 90 meters.
These tiles come in HGT format.

#. Compute SRTM tiles needed for transmitters
#. Download tiles
#. Create SPLAT! data files
#. Create coverage reports


Workflow 2
===========

Create coverage reports using NZSoSDEM tiles which provide a resolution of roughly 15 meters.
These tiles come in GeoTIFF format.

#. Compute NZSoSDEM tiles needed for transmitters
#. Download tiles
#. Clip NZSoSDEM tiles to same extent covered by SRTM tiles for transmitters
#. Convert NZSoSDEM tiles from GeoTIFF to HGT format
#. Create SPLAT! data files
#. Create coverage reports