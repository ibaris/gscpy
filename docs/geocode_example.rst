Geocoding Example
-----------------
After we downloaded the Sentinel 1 Files with ``ds1.download`` we want to geocode all the files automatically. Thus,
we start with command ``pr.geocode`` the geocode GUI. Now we can specify our directory where the sentinel data are:

.. image:: _static/pr_geocode_00.png
   :scale: 50 %
   :alt: input
   :align: center

After these we specify our output directory:

.. image:: _static/pr_geocode_0.png
   :scale: 50 %
   :alt: output
   :align: center

if we click on ``Run`` now the geocode processing will run with ESA´s SNAP software:

.. image:: _static/pr_geocode_2.png
   :scale: 50 %
   :alt: run
   :align: center

If there is any scene that is already processed the ``pr.geocode`` module will skip these files:

.. image:: _static/pr_geocode_1.png
   :scale: 50 %
   :alt: exist
   :align: center
