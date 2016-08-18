Wavetrace
**********
A Python 3.5 package designed to produce radio signal strength reports given radio transmitter data and topography data around the transmitters.
Uses `SPLAT! <http://www.qsl.net/kd2bd/splat.html>`_ to do the math.


Installation
============
1. Install SPLAT!, ImageMagick, and GDAL. For example, to install these on a Linux system do ``sudo apt-get update; sudo apt-get install splat imagemagick gdal-bin ``
2. Create a Python 3.5 virtual environment
3. In your virtual environment, install Wavetrace via Pip via ``pip install wavetrace``


Usage
======
Examples in the Jupyter notebook ``ipynb/examples.ipynb``.
Command-line interface coming soon.


Documentation
==============
In ``docs`` and on Rawgit `here <https://rawgit.com/araichev/wavetrace/develop/docs/_build/singlehtml/index.html>`_


Further Reading
================
- `SPLAT! documentation <http://www.qsl.net/kd2bd/splat.pdf>`_
- The Wikipedia article on the `Longley-Rice model <https://en.wikipedia.org/wiki/Longley-Rice_Model>`_ 
- The Open Street Map wiki page on `SRTM data <https://wiki.openstreetmap.org/wiki/SRTM>`_


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