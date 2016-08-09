Wavetrace
**********
A Python 3.5 module to produce radio signal strength reports given radio transmitter data and elevation data for the study region.
Uses `SPLAT! <http://www.qsl.net/kd2bd/splat.html>`_ to do the math.


Installation
============
1. Install SPLAT!, ImageMagick, and GDAL. For example, to install these on a Linux system do ``sudo apt-get update; sudo apt-get install splat imagemagick gdal-bin ``
2. Create a Python 3.5 virtual environment
3. In your virtual environment, install Wavetrace via Pip via ``pip install wavetrace``


Usage
======


Documentation
==============
In ``docs``.


Authors
=======
- Chris Guest (2013-06)
- Alex Raichev (2016-08)


References
=============
- `SPLAT! documentation <http://www.qsl.net/kd2bd/splat.pdf>`_
- `Shuttle Radio Topography Mission (SRTM) <https://en.wikipedia.org/wiki/SRTM>`_
- `SRTM HGT format <http://www.gdal.org/frmt_various.html#SRTMHGT>`_