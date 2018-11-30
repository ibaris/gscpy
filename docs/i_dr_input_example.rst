Import / Export Raster Files
----------------------------
After downloading the data (See section Data), you can list all available raster files within the directory
`climate_2000_2012`, by using the module ``i.dr.import``::

    $ i.dr.input -p input_dir=/media/ibaris/Shared/Documents/NC_DATA/climate_2000_2012

Now you can see all files:

.. image:: _static/i_dr_import_0.png
   :scale: 50 %
   :alt: Create a Mapset
   :align: center

To show the ``pattern`` parameter of the module ``i.dr.import`` we want to consider only files that has the string
`tempmean` in their filenames::

    $ i.dr.input -p input_dir=/media/ibaris/Shared/Documents/NC_DATA/climate_2000_2012 pattern=.*tempmean

.. image:: _static/i_dr_import_1.png
   :scale: 50 %
   :alt: Create a Mapset
   :align: center

With the command::

    $ i.dr.input input_dir=/media/ibaris/Shared/Documents/NC_DATA/climate_2000_2012

you can import all raster files located in `/media/ibaris/Shared/Documents/NC_DATA/climate_2000_2012`. To be sure
you can use the command::

    $ g.list type=raster

.. image:: _static/i_dr_import_4.png
   :scale: 50 %
   :alt: Create a Mapset
   :align: center

You could export all files with the command ``out.l.gdal`` like::

    $ out.l.gdal type=raster outdir=/media/ibaris/Shared/Documents/NC_DATA/climate_2000_2012

With the `flag: -p` you can see the files that will be exported:

.. image:: _static/out_l_gdal_0.png
   :scale: 50 %
   :alt: Create a Mapset
   :align: center
