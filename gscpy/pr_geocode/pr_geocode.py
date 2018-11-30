#!/usr/bin/env python

############################################################################
#
# MODULE:       pr.geocode
# AUTHOR(S):    Ismail Baris
# PURPOSE:      Wrapper function for geocoding SAR images pyroSAR.
#
# COPYRIGHT:    (C) Ismail Baris and Nils von Norsinski
#
#               This program is free software under the GNU General
#               Public License (>=v2). Read the file COPYING that
#               comes with GRASS for details.
#
#############################################################################

#%module
#% description: Wrapper function for geocoding SAR images using ESA SNAP.
#% keyword: processing
#% keyword: sar
#% keyword: sentinel 1
#%end

# Input Section --------------------------------------------------------------------------------------------------------
#%option G_OPT_M_DIR
#% key: input_dir
#% multiple: no
#% description: The directory where the files are located.
#%guisection: Input
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
#% required: yes
#% multiple: no
#% description: The directory to write the final files to:
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

# Filter Section -------------------------------------------------------------------------------------------------------
#%option
#% key: pattern
#% description: The pattern of file names.
#% guisection: Filter
#%end

#%option
#% key: polarizations
#% type: string
#% required: no
#% multiple: yes
#% description: The polarizations to be processed (Default is 'all'):
#% guisection: Filter
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

# Auto Import Section --------------------------------------------------------------------------------------------------
#%flag
#% key: i
#% description: Import processed files in a mapset.
#% guisection: Import
#%end

#%flag
#% key: r
#% description: Reproject raster data (using r.import if needed).
#% guisection: Import
#%end

#%flag
#% key: l
#% description: Link raster data instead of importing.
#% guisection: Import
#%end

#%option
#% key: pattern
#% description: The pattern of file names.
#% guisection: Import
#%end

# Mapset Section -------------------------------------------------------------------------------------------------------
#%flag
#% key: c
#% description: Create a new mapset.
#% guisection: Mapset
#%end

#%option
#% key: mapset
#% required: no
#% type: string
#% multiple: no
#% description: Name of mapset.
#%guisection: Mapset
#%end

#%option
#% key: location
#% type: string
#% multiple: no
#% required: no
#% description: Location name (not location path).
#%guisection: Mapset
#%end

#%option G_OPT_M_DIR
#% key: dbase
#% multiple: no
#% required: no
#% description: GRASS GIS database directory.
#%guisection: Mapset
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


import datetime as dt
import os
import re
import sys

from pyroSAR.snap.util import geocode

try:
    import grass.script as gs
    from grass.exceptions import CalledModuleError
except ImportError:
    raise ImportError("You must installed GRASS GIS to run this program.")

try:
    from osgeo import gdal, osr
except ImportError as e:
    gs.fatal(_("Parameter t_srs_from_file requires GDAL library: {}").format(e))

    raise ImportError("You must installed GRASS GIS to run this program.")


class Geocode(object):
    """
     Wrapper function for geocoding SAR images using pyroSAR.

     Parameters
     ----------
     input_dir: str
         Directory where the Sentinel-Data is.
     outdir: str
         The directory to write the final files to.
     t_srs: int, str or osr.SpatialReference
         A target geographic reference system in WKT, EPSG, PROJ4 or OPENGIS format.
         See function :func:`spatialist.auxil.crsConvert()` for details.
         Default: `4326 <http://spatialreference.org/ref/epsg/4326/>`_.
     resolution_value: int or float, optional
         The target resolution in meters. Default is 20
     polarizations: list or {'VV', 'HH', 'VH', 'HV', 'all'}, optional
         The polarizations to be processed; can be a string for a single polarization e.g. 'VV' or a list of several
         polarizations e.g. ['VV', 'VH']. Default is 'all'.
     shapefile: str or :py:class:`~spatialist.vector.Vector`, optional
         A vector geometry for subsetting the SAR scene to a test site. Default is None.
     scaling: {'dB', 'db', 'linear'}, optional
         Should the output be in linear or decibel scaling? Default is 'dB'.
     geocoding_type: {'Range-Doppler', 'SAR simulation cross correlation'}, optional
         The type of geocoding applied; can be either 'Range-Doppler' (default) or 'SAR simulation cross correlation'
     removeS1BoderNoise: bool, optional
         Enables removal of S1 GRD border noise (default).
     offset: tuple, optional
         A tuple defining offsets for left, right, top and bottom in pixels, e.g. (100, 100, 0, 0); this variable is
         overridden if a shapefile is defined. Default is None.
     external_dem_file: str or None, optional
         The absolute path to an external DEM file. Default is None.
     external_dem_nan: int, float or None, optional
         The no data value of the external DEM. If not specified (default) the function will try to read it from the
         specified external DEM.
     externalDEMApplyEGM: bool, optional
         Apply Earth Gravitational Model to external DEM? Default is True.
     basename_extensions: list of str
         names of additional parameters to append to the basename, e.g. ['orbitNumber_rel']
     test: bool, optional
         If set to True the workflow xml file is only written and not executed. Default is False.

     Attributes
     ----------
     files : list
         All detected files.

     Methods
     -------
     geocode()
         Start the geocoding process.
     import_products(pattern=None, mapset=None, dbase=None, location=None, flags=None)
         Import detected files.
     print_products()
         Print all detected files.

     Examples
     --------
     The general usage is
     ::
         $ pr.geocode [-e -i -r -l -c -p -t -b] input_dir=string outdir=string [pattern=string] [t_srs=string] [t_srs_from_file=string]
             [resolution_value=integer] [polarizations=string] [shapefile=string] [scaling=string]
             [geocoding_type=string] [offset=string] [external_dem_file=string] [external_dem_nan=integer]
             [basename_extensions=string] [mapset=string] [dbase=string] [location=string] [--verbose] [--quiet]


     Import Sentinel 1A files geocode and import them in current mapset and reproject it
     ::
         $ pr.geocode -r input_dir=/home/user/data outdir=/home/user/data/processed t_srs=43265

     Import Sentinel 1A files geocode and import them in a new mapset within another GRASS GIS database
     ::
         $ pr.geocode -r input_dir=/home/user/data outdir=/home/user/data/processed t_srs=43265 mapset=Goettingen dbase=/home/user/grassdata/germany

     Note
     ----
     If only one polarization is selected the results are directly written to GeoTiff.
     Otherwise the results are first written to a folder containing ENVI files and then transformed to GeoTiff files
     (one for each polarization).
     If GeoTiff would directly be selected as output format for multiple polarizations then a multilayer GeoTiff
     is written by SNAP which is considered an unfavorable format

     Notes
     -----
     **Flags:**
         * e : Apply Earth Gravitational Model to external DEM.
         * i : Import processed files in a mapset.
         * r : Reproject raster data (using r.import if needed).
         * l : Link raster data instead of importing.
         * c : Create a new mapset.
         * p : Print the detected files and exit.
         * t : Write only the workflow in xml file
         * b : Enables removal of S1 GRD border noise.

     """

    def __init__(self, input_dir, outdir, pattern=None, t_srs=None, t_srs_from_file=None, resolution_value=20,
                 polarizations='all', shapefile=None, scaling='dB', geocoding_type='Range-Doppler',
                 removeS1BoderNoise=True, offset=None, external_dem_file=None, external_dem_nan=None,
                 externalDEMApplyEGM=True, basename_extensions=None, test=False, verbose=False):

        # Check Georeference -------------------------------------------------------------------------------------------
        if t_srs is None and t_srs_from_file is None:
            raise ValueError("A EPSG code (t_srs) or a geocoded file (t_srs_from_file) must be defined.")

        elif t_srs is not None and t_srs_from_file is not None:
            raise ValueError("Parameter t_srs AND A t_srs_from_file are defined. EPSG code OR a geocoded "
                             "file must be defined.")
        else:
            if t_srs is not None:
                self.t_srs = int(t_srs)
            else:
                self.t_srs = None

            if t_srs_from_file is not None:
                if not os.path.exists(t_srs_from_file):
                    raise ValueError("File <{0}> does not exist".format(t_srs_from_file))

                else:
                    self.t_srs_from_file = t_srs_from_file
                    self.t_srs = self.__raster_epsg(self.t_srs_from_file)

            else:
                self.t_srs_from_file = None

        # Initialize Directory -----------------------------------------------------------------------------------------
        self._dir_list = []

        if not os.path.exists(input_dir):
            gs.fatal(_('Input directory <{}> not exists').format(input_dir))
        else:
            self.input_dir = input_dir

        if not os.path.exists(outdir):
            os.makedirs(outdir)
        else:
            self.outdir = outdir

        # Create Pattern and find files --------------------------------------------------------------------------------
        self.extension = '.zip'

        if pattern:
            filter_p = pattern + self.extension
        else:
            filter_p = r'.*.' + self.extension

        self.filter_p = filter_p

        gs.debug('Filter: {}'.format(filter_p), 1)
        self.files = self.__filter(filter_p)

        # Self definitions ---------------------------------------------------------------------------------------------
        self.t_srs = t_srs
        self.resolution_value = resolution_value
        self.polarizations = polarizations
        self.shapefile = shapefile
        self.scaling = scaling
        self.geocoding_type = geocoding_type
        self.removeS1BoderNoise = removeS1BoderNoise
        self.offset = offset
        self.external_dem_file = external_dem_file
        self.external_dem_nan = external_dem_nan
        self.externalDEMApplyEGM = externalDEMApplyEGM
        self.basename_extensions = basename_extensions
        self.test = test
        self.verbose = verbose

    # ------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------------------------------------------------------
    def geocode(self):
        """
        Start the geocode process.

        Returns
        -------
        None
        """
        for infile in self.files:
            sys.stdout.write('Start Time: {0} ----'.format(dt.datetime.utcnow().__str__()))
            sys.stdout.write('Start Processing File: <{0}> {1}'.format(str(os.path.basename(infile)), os.linesep))

            geocode(infile, self.outdir, t_srs=self.t_srs, tr=self.resolution_value, polarizations=self.polarizations,
                    shapefile=self.shapefile, scaling=self.scaling, geocoding_type=self.geocoding_type,
                    removeS1BoderNoise=self.removeS1BoderNoise, offset=self.offset,
                    externalDEMFile=self.external_dem_file, externalDEMNoDataValue=self.external_dem_nan,
                    externalDEMApplyEGM=self.externalDEMApplyEGM, test=self.test)

            sys.stdout.write('End Time: {0} ----'.format(dt.datetime.utcnow().__str__()))
            sys.stdout.flush()

    def import_products(self, pattern=None, mapset=None, dbase=None, location=None, flags=None):
        """
        Import all detected files in a mapset.

        Parameters
        ----------
        pattern : str, optional
            The pattern of file names. If not specified all files with selected extension will be imported.
        mapset : str, optional
            Name of mapset.
        dbase : str, optional
            Location of GRASS GIS database
        mapset : str, optional
            Name of the mapset that will be created.
        flags : str
            Available flags are '-c-r-l'

        Returns
        -------
        None
        """
        args = {'input': self.outdir, 'extension': 'GEOTIFF'}

        if pattern:
            args['pattern'] = pattern
        else:
            args['pattern'] = ''

        if mapset:
            args['mapset'] = mapset
        else:
            args['mapset'] = ''

        if dbase:
            args['dbase'] = dbase
        else:
            args['dbase'] = ''

        if location:
            args['location'] = location
        else:
            args['location'] = ''

        if flags:
            pass
        else:
            flags = ''

        module = 'i.dr.import'

        try:
            gs.run_command(module, flags=flags, input_dir=self.outdir, **args)

        except CalledModuleError as e:
            pass

    def print_products(self):
        """
        Print all detected files.

        Returns
        -------
        None
        """
        for f in self.files:
            sys.stdout.write('Detected File <{0}> {1}'.format(str(f), os.linesep))

    # ------------------------------------------------------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------------------------------------------------------
    def __filter(self, filter_p):
        pattern = re.compile(filter_p)
        files = []
        for rec in os.walk(self.input_dir):
            if not rec[-1]:
                continue

            match = filter(pattern.match, rec[-1])
            if match is None:
                continue

            for f in match:
                if f.endswith(self.extension):
                    files.append(os.path.join(rec[0], f))

        return files

    def __raster_epsg(self, filename):
        dsn = gdal.Open(filename)

        srs = osr.SpatialReference()
        srs.ImportFromWkt(dsn.GetProjectionRef())

        ret = srs.GetAuthorityCode(None)
        dsn = None

        return ret


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


def main():
    if options['t_srs'] is None:
        options['t_srs'] = 4326
    else:
        options['t_srs'] = int(options['t_srs'])

    if options['resolution_value'] is None:
        options['resolution_value'] = 20

    if options['geocoding_type'] is 'Cross-Correlation':
        options['geocoding_type'] = 'SAR simulation cross correlation'

    if options['polarizations'] is None:
        options['polarizations'] = 'all'

    if options['offset'] is not None:
        offset_list = options['offset'].split(',')
        offset_list = [int(item) for item in offset_list]
        options['offset'] = tuple(offset_list)

    pp_geocode = Geocode(input_dir=options['input_dir'], outdir=options['outdir'], pattern=options['pattern'],
                         t_srs=options['t_srs'], resolution_value=options['resolution_value'],
                         polarizations=options['polarizations'], shapefile=options['shapefile'],
                         scaling=options['scaling'], geocoding_type=options['geocoding_type'],
                         removeS1BoderNoise=flags['b'], offset=options['offset'],
                         external_dem_file=options['external_dem_file'], external_dem_nan=options['external_dem_nan'],
                         externalDEMApplyEGM=flags['e'], test=flags['t'])

    if flags['p']:
        pp_geocode.print_products()
        return 0

    pp_geocode.geocode()

    if flags['i']:
        pattern = options['pattern']
        mapset = options['mapset']
        dbase = options['dbase']
        location = options['location']

        flag = ''
        flag_list = ['c', 'r', 'l']

        for item in flag_list:
            if flags[item]:
                flag += item
            else:
                pass

        pp_geocode.import_products(pattern=pattern, mapset=mapset, dbase=dbase, location=location, flags=flags)

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    options = change_dict_value(options, '', None)
    sys.exit(main())
