Examples
========
Here are some examples of how you can use the gscpy package with GRASS GIS. In the examples most of the modules are
executed within the GRASS terminal. It is also possible to do all these steps with the graphical GUI. Most of the
examples are from `FOSS4G 2014 workshop`_

.. _FOSS4G 2014 workshop: http://ncsu-geoforall-lab.github.io/grass-temporal-workshop/


Data
----
These data are from `here`_. These data are already in a GRASS GIS database. To show the import routines I exported the
files within the mapset `climate_2000_2012` with `out.l.gdal`. This mapset contains temperature and precipitation series
for North Carolina from `State Climate Office of North Carolina`_.


.. _here: http://fatra.cnr.ncsu.edu/temporal-grass-workshop/NC_spm_temporal_workshop.zip
.. _State Climate Office of North Carolina: http://convection.meas.ncsu.edu:8080/thredds/catalog/catalog.html

Contents
--------


.. toctree::
   :maxdepth: 2
   :titlesonly:

   data
   g_c_mapset_example
   ds1_download_example
   geocode_example
   sentinel_finder_example
   t_c_register_sentinel_example
   t_raster_mapcalc_example
   i_dr_input_example
   t_c_register_example
   pchain

