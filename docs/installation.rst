Installation
============
After you have received the `gscpy` package, you can install it with
::
    $ python setup.py install

After this process it is advantageous to use the script ``i_script`` with GRASS GIS. This is necessary because some
modules from this package call other modules from this package that are only present if they are located in the
script folder of GRASS GIS. It is possible that some of these modules require administration rights. The reason for
this is that, for example, when downloading data to the hard disk, any write permissions must be present. Thus,
here the launch process is proceeded with ``sudo``::
    $ sudo grass

To launch a Python script from GUI, use File -> Launch Python script and select /path/to/gscpy/i_script.py.

Now you can launch the following modules:
    * i.script: A simple module that import Scripts from a package to GRASS GIS script directory.
    * g.database: Create a GRASS GIS Database.
    * g.c.mapset: Create a mapset in a GRASS GIS Database if it is not existent.
    * s1.download: Data download including basic adjustments for Sentinel-1 with `sentinelsat`_.
    * i.dr.import: Import data into a mapset from a file with considering a certain pattern.
    * i.fr.import: Import pyroSAR dataset in a directory based on their metadata.
    * pr.geocode: Wrapper function for geocoding SAR images using `pyroSAR`_.
    * t.c.register: Creation of Sentinel-1 space-time cube.

.. _pyroSAR: https://github.com/johntruckenbrodt/pyroSAR
.. _sentinelsat: https://github.com/sentinelsat/sentinelsat