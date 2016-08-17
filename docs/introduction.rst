Introduction
*************
Wavetrace is a Python 3.5 package designed to produce radio signal strength reports given radio transmitter data and topography data around the transmitters.
It uses `SPLAT! <http://www.qsl.net/kd2bd/splat.html>`_ to predict the attenuation of radio signals, which implements a `Longley-Rice model <https://en.wikipedia.org/wiki/Longley%E2%80%93Rice_model>`_. 
 

Installation
============
1. Install SPLAT!, ImageMagick, and GDAL. For example, to install these on a Linux system do ``sudo apt-get update; sudo apt-get install splat imagemagick gdal-bin ``
2. Create a Python 3.5 virtual environment
3. In your virtual environment, install Wavetrace via Pip via ``pip install wavetrace``


Usage
=========
#. Create a CSV file containing transmitter data
#. Download SRTM3 (standard definition) or SRTM1 (high definition) topography data for the regions surrounding the transmitters
#. Create SPLAT! data files
#. Create coverage reports


Further Reading
================
- `SPLAT! documentation <http://www.qsl.net/kd2bd/splat.pdf>`_
- `Open Street Map wiki page on SRTM data <https://wiki.openstreetmap.org/wiki/SRTM>`_


Authors
=======
- Chris Guest (2013-06)
- Alex Raichev (2016-08)