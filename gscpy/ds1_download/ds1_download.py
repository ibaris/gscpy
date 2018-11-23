#!/usr/bin/env python

############################################################################
#
# MODULE:       d.s1.download
# AUTHOR(S):    Nils von Norsinski, Ismail Baris
# PURPOSE:      Download Sentinel Data.
#
# COPYRIGHT:    (C) Ismail Baris and Nils von Norsinski
#
#               This program is free software under the GNU General
#               Public License (>=v2). Read the file COPYING that
#               comes with GRASS for details.
#
#############################################################################

#%module
#% description: Download Sentinel Data
#% keyword: imagery
#% keyword: satellite
#% keyword: Sentinel
#% keyword: download
#%end

# Input Section --------------------------------------------------------------------------------------------------------
#%option
#% key: username
#% description: Username for Copernicus Open Acces Hub.
#% required: yes
#%guisection: User
#%end

#%option
#% key: password
#% description:  Password for Copernicus Open Access Hub.
#% required: yes
#%guisection: User
#%end

# Output Section --------------------------------------------------------------------------------------------------------
#%option G_OPT_M_DIR
#% key: outdir
#% description: The directory where the files will be downloaded.
#% required: yes
#%guisection: Output
#%end

# Subset Section -------------------------------------------------------------------------------------------------------
#%option G_OPT_F_INPUT
#% key: region
#% type: string
#% description: Choose geojson file to define the observation area.
#%guisection: Region
#%end

# Time Section ---------------------------------------------------------------------------------------------------------
#%option
#% key: timestart
#% description: Starting time of observation period (YYYY-MM-DD).
#% required: yes
#%guisection: Time
#%end

#%option
#% key: timeend
#% description: End time of observation period (YYYY-MM-DD).
#% required: yes
#%guisection: Time
#%end


# Sensor Section -------------------------------------------------------------------------------------------------------
#%option
#% key: polarisationmode
#% required: no
#% multiple: yes
#% description: Choose the polarisationmode (Default is all).
#%guisection: Sensor
#%end

# Orbit Section -------------------------------------------------------------------------------------------------------
#%option
#% key: orbitnumber
#% type: integer
#% required: no
#% description: Choose the orbitnumber.
#%guisection: Orbit
#%end

#%option
#% key: orbitdirection
#% required: no
#% description: Choose a orbit direction.
#% answer: ALL
#% options: ALL, DESCENDING, ASCENDING
#%guisection: Orbit
#%end

# Product Section ------------------------------------------------------------------------------------------------------
#%option
#% key: producttype
#% answer: All
#% options: All, SLC, GRD, OCN, RAW
#% description: Choose the product type.
#%guisection: Product
#%end

#%option
#% key: sensoroperationalmode
#% required: no
#% answer: All
#% options: All, SM, IW, EW, WV
#% description: Choose the sensoroperationalmode.
#%guisection: Product
#%end


# Optional Section -----------------------------------------------------------------------------------------------------
#%flag
#% key: p
#% description: Print the detected files and exit.
#% guisection: Optional
#%end


import os
import sys

try:
    import grass.script as gs
except ImportError:
    raise ImportError("You must installed GRASS GIS to run this program.")

from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt


class S1Download(object):
    """
    This module makes searching, downloading and retrieving the metadata of Sentinel satellite images from the
    Copernicus Open Access Hub easy.

    Parameters
    ----------
    username : str
        Username for Copernicus Open Access Hub
    password : str
        Password for Copernicus Open Access Hub
    region : str
        A geojson file.
    timestart : str
        Start time like "YYYY-MM-DD"
    timeend : str
        End time like "YYYY-MM-DD".
    outdir : str
        Output directory.
    producttype : {'SLC', 'GRD', 'OCN', ''RAW}
        Product type. If None, all types will be recognized.
    polarisationmode tuple or str
        A combination of V and H like ('VH', 'HV') or simple 'VH'.
    sensoroperationalmode : {'SM', 'IW', 'EW', 'WV'}
        Sensor operational mode. If None, all types will be recognized.
    orbitnumber : int
        Orbit number
    orbitdirection : {DESCENDING, ASCENDING}
        Orbit direction. If None, all types will be recognized.

    Attributes
    ----------
    api : object
        Sentinelsat API object.
    outdir : str
    region : wkt
        A geojson to WKT object.
    kwargs : dict
        Dictionary with setted attributes.
    files : DataFrame
        Pandas DataFrame with detected files.

    Methods
    -------
    download()
        Download all files.
    print_products()
        Print all detected files.

    Examples
    --------
    The general usage is
    ::
        $ ds1.download [-p] username=string password=string region=string timestart=string timeend=string outdir=sting
        [*attributes=string] [--verbose] [--quiet]

    For *attributes the following parameters can be used
    ::
        >>> ["producttype", "polarisationmode", "sensoroperationalmode", "orbitnumber", "orbitdirection"]

    Print all Sentinel 1 data with product type GRD between 2015-01-02 and 2015-01-12::
        $ ds1.download -p username=DALEK password=exterminate region=myGEoJsOnFile.geojson timestart=2015-01-02
        timeend=2015-01-12 outdir='home/usr/data' producttype=SLC

    Download the last query
    ::
        $ ds1.download username=DALEK password=exterminate region=myGEoJsOnFile.geojson timestart=2015-01-02
        timeend=2015-01-12 outdir='home/usr/data' producttype=SLC

    Notes
    -----
    **Flags:**
        * p : Print the detected files and exit.
    """
    def __init__(self, username, password, region, timestart, timeend, outdir, producttype=None, polarisationmode=None,
                 sensoroperationalmode=None, orbitnumber=None, orbitdirection=None):

        # Inititalise Sentinel Python API ------------------------------------------------------------------------------
        self.api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')

        # Initialize Directory -----------------------------------------------------------------------------------------
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        else:
            self.outdir = outdir

        # Initialise Mandatory Parameter ------------------------------------------------------------------------------
        self.region = geojson_to_wkt(read_geojson(region))

        # < Reformat Time > ------------
        timestart_split = timestart.split('-')

        timestart_temp = ''
        for item in timestart_split:
            timestart_temp += item

        timeend_split = timeend.split('-')

        timeend_temp = ''
        for item in timeend_split:
            timeend_temp += item

        self.date = (timestart_temp, timeend_temp)

        # Initialize Attributes ----------------------------------------------------------------------------------------
        input_parameter = [producttype, polarisationmode, sensoroperationalmode, orbitnumber, orbitdirection]
        __KEYS__ = ["producttype", "polarisationmode", "sensoroperationalmode", "orbitnumber", "orbitdirection"]

        self.kwargs = {}

        for i, item in enumerate(input_parameter):
            if item is not None:
                self.kwargs[__KEYS__[i]] = item

        # Inititalise Sentinel Producs with API ------------------------------------------------------------------------
        self.products = self.api.query(self.region, date=self.date, platformname='Sentinel-1', **self.kwargs)

        self.files = self.api.to_dataframe(self.products)

    def download(self):
        self.api.download_all(self.products, directory_path=self.outdir)
        return 0

    def print_products(self):
        """
        Print all detected files.

        Returns
        -------
        None
        """

        df = self.files.to_string()
        sys.stdout.write(df)


def change_dict_value(dictionary, old_value, new_value):
    """
    Change a certain value from a dictionary.

    Parameters
    ----------
    dictionary : dict
        Input dictionary.
    old_value : str, NoneType, bool
        The value to be changed.
    new_value : str, NoneType, bool
        Replace value.

    Returns
    -------
    dict
    """
    for key, value in dictionary.items():
        if value == old_value:
            dictionary[key] = new_value

    return dictionary


def tuple_multi_string(dictionary, sep=','):
    """
    Convert values like 'a, b' to ('a', 'b').

    Parameters
    ----------
    dictionary : dict
        Input dictionary.
    sep : str
        Seperator

    Returns
    -------
    dict
    """
    for key, value in dictionary.items():
        value_split = value.split(sep)

        if len(value_split) == 1 or len(value_split) == 0:
            pass
        else:
            dictionary[key] = tuple(value_split)

    return dictionary


def main():
    region = os.path.normpath(options['region'])
    region = region.split("\\")
    regs = ""

    for i in region:
        regs = regs + i + "\\" + "\\"

    regs = regs[:-2]
    options['region'] = regs

    downloader = S1Download(username=options['username'], password=options['password'], region=options['region'],
                            timestart=options['timestart'], timeend=options['timeend'], outdir=options['outdir'],
                            producttype=options['producttype'], polarisationmode=options['polarisationmode'],
                            sensoroperationalmode=options['sensoroperationalmode'],
                            orbitnumber=options['orbitnumber'], orbitdirection=options['orbitdirection'])

    if flags['p']:
        downloader.print_products()
        return 0

    downloader.download()

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    options = tuple_multi_string(options)
    options = change_dict_value(options, '', None)
    options = change_dict_value(options, 'ALL', None)
    options = change_dict_value(options, 'All', None)

    sys.exit(main())
