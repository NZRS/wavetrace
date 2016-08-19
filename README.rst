Wavetrace
*************
Wavetrace is a Python 3.5 package designed to produce radio signal coverage reports given radio transmitter data and topography data around the transmitters.
It uses `SPLAT! <http://www.qsl.net/kd2bd/splat.html>`_ to predict the attenuation of radio signals, which implements a `Longley-Rice model <https://en.wikipedia.org/wiki/Longley%E2%80%93Rice_model>`_.
The package is intended for use in New Zealand but can be configured to work elsewhere on Earth. 
 

Installation
============
1. Install SPLAT!, ImageMagick, and GDAL. For example, to install these on a Linux system do ``sudo apt-get update; sudo apt-get install splat imagemagick gdal-bin ``
2. Create a Python 3.5 virtual environment
3. In your virtual environment, install Wavetrace via Pip via ``pip install wavetrace``


Usage
=========
Here is a common workflow.

#. Create a CSV file containing transmitter data
#. Process the transmitter data
#. Download SRTM3 (standard definition) or SRTM1 (high definition) topography data for the regions around the transmitters
#. Process the topography data
#. Compute radio signal coverage reports from the processed transmitter and topography data 

More details soon...


Documentation
==============
In ``docs`` and on Rawgit `here <https://rawgit.com/araichev/wavetrace/develop/docs/_build/singlehtml/index.html>`_


Further Reading
================
- `SPLAT! documentation <http://www.qsl.net/kd2bd/splat.pdf>`_
- `Open Street Map wiki page on SRTM data <https://wiki.openstreetmap.org/wiki/SRTM>`_


Authors
=======
- Chris Guest (2013-06)
- Alex Raichev (2016-08)


Changelog
==========

v2.0.0, 2016-08
----------------
- Complete refactor as a Python package


v1.0.0, 2013?
--------------
- Initial version 