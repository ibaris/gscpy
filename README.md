<h1 align="center">
  <br>
  <a href="https://gscpy.readthedocs.io/en/latest/#"><img src="https://i.imgur.com/uShXZIF.png" alt="GSCPY" width="400"></a>
</h1>
<h4 align="center">Sentinel-1 SAR Pre-Processing in GRASS GIS </h4>

<p align="center">
  <a href="http://forthebadge.com">
    <img src="http://forthebadge.com/images/badges/made-with-python.svg"
         alt="Gitter">
  </a>
  <a href="http://forthebadge.com"><img src="http://forthebadge.com/images/badges/built-with-love.svg"></a>
  <a href="http://forthebadge.com">
      <img src="http://forthebadge.com/images/badges/built-with-science.svg">
  </a>
</p>


<p align="center">
  <a href="#description">Description</a> •
  <a href="#installation">Installation</a> •
  <a href="#documentation">Doumentation</a> •
  <a href="#authors">Author</a> •
  <a href="#acknowledgments">Acknowledgments</a>
</p>

<p align="center">
    <a href='https://gscpy.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://readthedocs.org/projects/gscpy/badge/?version=latest' alt='Documentation Status' />
    </a>
</p>

# Description
The goal is the development of Python GRASS modules for the automatic download, processing and analysis of Sentinel-1
data. All modules can be executed in GRASS or in a terminal. The aim of this work was that a user can process all data
without much effort and import them directly into GRASS GIS for further analysis. By entering certain metadata you can
use this module to search for newly processed files and import them into a database.


Here is an overview of the content:
* A simple module that import Scripts from a package to GRASS GIS script directory.
* Database management modules where one can create entire databases or mapsets.
* Data download including basic adjustments for Sentinel-1 with <a href="https://github.com/sentinelsat/sentinelsat"> sentinelsat</a>.
* A SAR pre-processing add-on for GRASS GIS based on SNAP processing workflow which uses <a href="https://github.com/johntruckenbrodt/pyroSAR"> pyroSAR</a>.
* Modules to import all files in a directory with considering a certain pattern.  Moreover, it is possible to import
      these data in different ``mapsets``.
* Module that can import ``pyroSAR`` dataset in a directory based on their metadata.
* Creation of Sentinel-1 space-time cube.
* Multi-temporal analysis using t.rast.mapcalc or t.rast.algebra.

The package <a href="https://github.com/johntruckenbrodt/pyroSAR"> pyroSAR</a> and <a href="https://github.com/sentinelsat/sentinelsat"> sentinelsat</a> is used for the pre-processing and download of sentinel data respectively.

## Modules
This packages include the following modules:
* i.script: A simple module that import Scripts from a package to GRASS GIS script directory.
* g.database: Create a GRASS GIS Database.
* g.c.mapset: Create a mapset in a GRASS GIS Database if it is not existent.
* s1.download: Data download including basic adjustments for Sentinel-1 with <a href="https://github.com/sentinelsat/sentinelsat"> sentinelsat</a>.
* i.dr.import: Import data into a mapset from a file with considering a certain pattern.
* i.fr.import: Import pyroSAR dataset in a directory based on their metadata.
* pr.geocode: Wrapper function for geocoding SAR images using <a href="https://github.com/johntruckenbrodt/pyroSAR"> pyroSAR</a>.
* c.std.create: Creation of Sentinel-1 space-time cube.
* a.analyse: Multi-temporal analysis using t.rast.mapcalc or t.rast.algebra.

# Installation
After you have received the `gscpy` package, you can install it with::

    $ python setup.py install

After this process it is advantageous to use the script `i_script` with GRASS GIS. This is necessary because some
modules from this package call other modules from this package that are only present if they are located in the
script folder of GRASS GIS. It is possible that some of these modules require administration rights. The reason for
this is that, for example, when downloading data to the hard disk, any write permissions must be present. Thus,
here the launch process is proceeded with `sudo`::

    $ sudo grass

To launch a Python script from GUI, use File -> Launch Python script and select /path/to/gscpy/i_script.py.

# Documentation
You can find the full documentation <a href="https://gscpy.readthedocs.io/en/latest/#">here</a>.

# Built With
* Python 2.7 (But it works with Python 3.5 as well)
* Requirements: grass, pyroSAR, sentinelsat

# Authors
* **Ismail Baris** - *Initial work* - (i.baris@outlook.de)
* **Nils v. Norsinski**

## Acknowledgments
*  <a href="https://github.com/johntruckenbrodt">John Truckenbrodt </a>

---

> ResearchGate [@Ismail_Baris](https://www.researchgate.net/profile/Ismail_Baris) &nbsp;&middot;&nbsp;
> Code::Stats [@Ismail_Baris](https://codestats.net/users/ibaris) &nbsp;&middot;&nbsp;
> GitHub [@ibaris](https://github.com/ibaris) &nbsp;&middot;&nbsp;
> Instagram [@ism.baris](https://www.instagram.com/ism.baris/)
