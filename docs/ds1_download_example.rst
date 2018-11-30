Sentinel 1 Downloader
---------------------
Here is an example of how to use the Sentinel downloader, to map all available data `(flag: -p)`::

    $ ds1.download -p username=DALEK password=exterminate region=myGEoJsOnFile.geojson timestart=2015-01-02
      timeend=2015-01-12 outdir='home/usr/data' producttype=SLC

Another way is to use the GUI:

Type your Username and Password:

.. image:: _static/ds1_download_0.png
   :scale: 50 %
   :alt: Create a Mapset
   :align: center

After the definition of a region with a geojson file you can specify the sensing period, polarization and the
product type:

.. image:: _static/ds1_download_1.png
   :scale: 50 %
   :alt: Create a Mapset
   :align: center

.. image:: _static/ds1_download_2.png
   :scale: 50 %
   :alt: Create a Mapset
   :align: center

.. image:: _static/ds1_download_3.png
   :scale: 50 %
   :alt: Create a Mapset
   :align: center

With `flag -p` you can print all available products. If the flag is missing all data will be downloaded:

.. image:: _static/ds1_download_4.png
   :scale: 50 %
   :alt: Create a Mapset
   :align: center
