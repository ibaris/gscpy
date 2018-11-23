Introduction
============
The goal is the development of Python GRASS modules for the automatic download, processing and analysis of Sentinel-1
data. All modules can be executed in GRASS or in a terminal. The aim of this work was that a user can process all data
without much effort and import them directly into GRASS GIS for further analysis. By entering certain metadata you can
use this module to search for newly processed files and import them into a database.


Here is an overview of the content:

    * A simple module that import Scripts from a package to GRASS GIS script directory.
    * Database management modules where one can create entire databases or mapsets.
    * Data download including basic adjustments for Sentinel-1 with `sentinelsat`_.
    * A SAR pre-processing add-on for GRASS GIS based on SNAP processing workflow which uses `pyroSAR`_.
    * Modules to import all files in a directory with considering a certain pattern.  Moreover, it is possible to import
      these data in different ``mapsets``.
    * Module that can import ``pyroSAR`` dataset in a directory based on their metadata.
    * Creation of Sentinel-1 space-time cube.
    * Multi-temporal analysis using t.rast.mapcalc or t.rast.algebra.

The package `pyroSAR`_ and `sentinelsat`_ is used for the pre-processing and download of sentinel data respectively.

Modules
-------
This packages include the following modules:
    * i.script: A simple module that import Scripts from a package to GRASS GIS script directory.
    * g.database: Create a GRASS GIS Database.
    * g.c.mapset: Create a mapset in a GRASS GIS Database if it is not existent.
    * s1.download: Data download including basic adjustments for Sentinel-1 with `sentinelsat`_.
    * i.dr.import: Import data into a mapset from a file with considering a certain pattern.
    * i.fr.import: Import pyroSAR dataset in a directory based on their metadata.
    * c.std.create: Creation of Sentinel-1 space-time cube.
    * a.analyse: Multi-temporal analysis using t.rast.mapcalc or t.rast.algebra.

.. _pyroSAR: https://github.com/johntruckenbrodt/pyroSAR
.. _sentinelsat: https://github.com/sentinelsat/sentinelsat