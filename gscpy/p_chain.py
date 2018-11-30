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
"""
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

#%option G_OPT_F_INPUT
#% key: t_srs_file
#% multiple: no
#% required: no
#% description: Using a georeferenced raster or vector file:
#%guisection: Input
#%end

#%option
#% key: t_srs
#% required: no
#% type: integer
#% multiple: no
#% description: A target geographic reference system in EPSG:
#%guisection: Input
#%end

#%option
#% key: geocoding_type
#% type: string
#% required: no
#% multiple: no
#% answer: Range-Doppler
#% options: Range-Doppler, Cross-Correlation
#% description: The type of geocoding applied:
#% guisection: Input
#%end

# Output Section -------------------------------------------------------------------------------------------------------
#%option G_OPT_M_DIR
#% key: outdir
#% description: The directory where the files will be downloaded.
#% required: yes
#%guisection: Output
#%end

#%option
#% key: resolution_value
#% type: double
#% required: no
#% multiple: no
#% description: Resolution of output raster map:
#% guisection: Output
#%end

#%option
#% key: scaling
#% type: string
#% required: no
#% multiple: no
#% answer: dB
#% options: dB,linear
#% description: Should the output be in linear or decibel scaling?:
#% guisection: Output
#%end

# Subset Section -------------------------------------------------------------------------------------------------------
#%option G_OPT_F_INPUT
#% key: region
#% type: string
#% description: Choose geojson file to define the observation area.
#%guisection: Subset
#%end

#%option
#% key: offset
#% type: integer
#% required: no
#% multiple: yes
#% description: Integers defining offsets for left, right, top and bottom in pixels, e.g. 100, 100, 0, 0:
#% guisection: Subset
#%end

#%option G_OPT_F_INPUT
#% key: shapefile
#% required: no
#% multiple: no
#% description: A vector geometry for subsetting the SAR scene to a test site:
#%guisection: Subset
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

# DEM Section ----------------------------------------------------------------------------------------------------------
#%flag
#% key: e
#% description: Apply Earth Gravitational Model to external DEM?
#% guisection: DEM
#%end

#%option G_OPT_F_INPUT
#% key: external_dem_file
#% required: no
#% multiple: no
#% description: The absolute path to an external DEM file:
#%guisection: DEM
#%end

#%option
#% key: external_dem_nan
#% type: integer
#% required: no
#% multiple: no
#% description: The no data value of the external DEM:
#% guisection: DEM
#%end

# Optional Section -----------------------------------------------------------------------------------------------------
#%flag
#% key: p
#% description: Print the detected files and exit.
#% guisection: Optional
#%end

#%flag
#% key: t
#% description: Write only the workflow in xml file
#% guisection: Optional
#%end

#%flag
#% key: b
#% description: Enables removal of S1 GRD border noise
#% guisection: Optional
#%end

"""
import sys

try:
    import grass.script as gs
    from grass.exceptions import CalledModuleError
except ImportError:
    raise ImportError("You have to install GRASS GIS to run this program.")

try:
    from osgeo import gdal, osr
except ImportError as e:
    gs.fatal(_("Flag -r requires GDAL library: {}").format(e))

    raise ImportError("You have to install GRASS GIS to run this program.")


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
    __DOWNLOAD_OPT__ = {'username': options['username'], 'password': options['password'], 'region': options['region'],
                        'timestart': options['timestart'], 'timeend': options['timeend'], 'outdir': options['outdir'],
                        'producttype': options['producttype'], 'polarisationmode': options['polarisationmode'],
                        'sensoroperationalmode': options['sensoroperationalmode'],
                        'orbitnumber': options['orbitnumber'], 'orbitdirection': options['orbitdirection']}

    __DOWNLOAD_FLAG__ = {'p': flags['p']}

    __GEOCODE_OPT__ = {'input_dir': options['input_dir'], 'outdir': options['outdir'], 'pattern': options['pattern'],
                       't_srs': options['t_srs'], 'resolution_value': options['resolution_value'],
                       'polarizations': options['polarizations'], 'shapefile': options['shapefile'],
                       'scaling': options['scaling'], 'geocoding_type': options['geocoding_type'],
                       'removeS1BoderNoise': flags['b'], 'offset': options['offset'],
                       'external_dem_file': options['external_dem_file'],
                       'external_dem_nan': options['external_dem_nan'],
                       'externalDEMApplyEGM': flags['e'], 'test': flags['t']}

    __DOWNLOAD_FLAG__ = {'i': flags['i'], 'p': flags['p']}

    gs.run_command('ds1.download', flags=__DOWNLOAD_FLAG__, **__DOWNLOAD_OPT__)
    gs.run_command('pr.geocode', flags=__DOWNLOAD_FLAG__, **__GEOCODE_OPT__)

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    options = tuple_multi_string(options)
    options = change_dict_value(options, '', None)
    options = change_dict_value(options, 'ALL', None)
    options = change_dict_value(options, 'All', None)

    options['input_dir'] = options['outdir']
    flags['i'] = True

    sys.exit(main())
