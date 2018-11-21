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

"""
#%module
#% description: Wrapper function for geocoding SAR images using ESA SNAP.
#% keyword: processing
#% keyword: sar
#% keyword: sentinel 1
#%end

# Input Section --------------------------------------------------------------------------------------------------------
#%option G_OPT_M_DIR
#% key: dir
#% multiple: no
#% description: Name for input directory where the processed data is:
#%guisection: Input
#%end

#%option
#% key: epsg
#% required: no
#% multiple: no
#% description: A target geographic reference system in EPSG, (Default is 4326):
#%guisection: Input
#%end

# Output Section -------------------------------------------------------------------------------------------------------
#%option G_OPT_M_DIR
#% key: outdir
#% required: no
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

#%option
#% key: geocoding_type
#% type: string
#% required: no
#% multiple: no
#% answer: Range-Doppler
#% options: Range-Doppler, Cross-Correlation
#% description: The type of geocoding applied:
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
#% description: File name pattern to import
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
#% description: Import processed imagery to a mapset
#% guisection: Import
#%end

#%option
#% key: pattern
#% description: File name pattern to import:
#% guisection: Import
#%end

#%flag
#% key: r
#% description: Reproject raster data using r.import if needed
#% guisection: Import
#%end

#%flag
#% key: l
#% description: Link raster data instead of importing
#% guisection: Import
#%end

# Optional Section -----------------------------------------------------------------------------------------------------
#%flag
#% key: p
#% description: Print raster data to be imported and exit
#% guisection: Optional
#%end

#%flag
#% key: t
#% description: Write only the workflow in xml file
#% guisection: Optional
#%end

#%flag
#% key: r
#% description: Enables removal of S1 GRD border noise
#% guisection: Optional
#%end
"""

import datetime as dt
import os
import re
import sys

import grass.script as gs
from pyroSAR.snap.util import geocode

try:
    import grass.script as gs
    from grass.exceptions import CalledModuleError
except ImportError:
    pass


class Geocode(object):
    def __init__(self, dir, outdir, pattern=None, t_srs=4326, tr=20, polarizations='all', shapefile=None, scaling='dB',
                 geocoding_type='Range-Doppler', removeS1BoderNoise=True, offset=None, externalDEMFile=None,
                 externalDEMNoDataValue=None, externalDEMApplyEGM=True, basename_extensions=None, test=False,
                 verbose=False):
        """
        Wrapper function for geocoding SAR images using pyroSAR.

        Parameters
        ----------
        dir: str
            Directory where the Sentinel-Data is.
        outdir: str
            The directory to write the final files to.
        t_srs: int, str or osr.SpatialReference
            A target geographic reference system in WKT, EPSG, PROJ4 or OPENGIS format.
            See function :func:`spatialist.auxil.crsConvert()` for details.
            Default: `4326 <http://spatialreference.org/ref/epsg/4326/>`_.
        tr: int or float, optional
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
        externalDEMFile: str or None, optional
            The absolute path to an external DEM file. Default is None.
        externalDEMNoDataValue: int, float or None, optional
            The no data value of the external DEM. If not specified (default) the function will try to read it from the
            specified external DEM.
        externalDEMApplyEGM: bool, optional
            Apply Earth Gravitational Model to external DEM? Default is True.
        basename_extensions: list of str
            names of additional parameters to append to the basename, e.g. ['orbitNumber_rel']
        test: bool, optional
            If set to True the workflow xml file is only written and not executed. Default is False.

        Note
        ----
        If only one polarization is selected the results are directly written to GeoTiff.
        Otherwise the results are first written to a folder containing ENVI files and then transformed to GeoTiff files
        (one for each polarization).
        If GeoTiff would directly be selected as output format for multiple polarizations then a multilayer GeoTiff
        is written by SNAP which is considered an unfavorable format

        See Also
        --------
        :class:`pyroSAR.drivers.ID`,
        :class:`spatialist.vector.Vector`,
        :func:`spatialist.auxil.crsConvert()`
        """

        # Initialize Directory -----------------------------------------------------------------------------------------
        self._dir_list = []

        if not os.path.exists(dir):
            gs.fatal(_('Input directory <{}> not exists').format(dir))
        else:
            self.dir = dir

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
        self.tr = tr
        self.polarizations = polarizations
        self.shapefile = shapefile
        self.scaling = scaling
        self.geocoding_type = geocoding_type
        self.removeS1BoderNoise = removeS1BoderNoise
        self.offset = offset
        self.externalDEMFile = externalDEMFile
        self.externalDEMNoDataValue = externalDEMNoDataValue
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
            if self.verbose:
                sys.stdout.write('Start Time: {0} ----'.format(dt.datetime.utcnow().__str__()))
                sys.stdout.write('Start Processing File: <{0}> {1}'.format(str(os.path.basename(infile)), os.linesep))

            geocode(infile, self.outdir, t_srs=self.t_srs, tr=self.tr, polarizations=self.polarizations,
                    shapefile=self.shapefile, scaling=self.scaling, geocoding_type=self.geocoding_type,
                    removeS1BoderNoise=self.removeS1BoderNoise, offset=self.offset,
                    externalDEMFile=self.externalDEMFile, externalDEMNoDataValue=self.externalDEMNoDataValue,
                    externalDEMApplyEGM=self.externalDEMApplyEGM, test=self.test)

            if self.verbose:
                sys.stdout.write('End Time: {0} ----'.format(dt.datetime.utcnow().__str__()))
                sys.stdout.flush()

    def import_products(self, pattern=None, f=False, l=False, p=False):
        """
        Import the processed data into a mapset.

        Parameters
        ----------
        pattern
        f
        l
        p

        Returns
        -------

        """
        args = {}
        args['input'] = self.dir
        args['f'] = f
        args['l'] = l
        args['p'] = p
        args['extension'] = 'GEOTIFF'

        if pattern:
            args['pattern'] = pattern
        else:
            args['pattern'] = ''

        module = 'i.s1.import'

        try:
            gs.run_command(module, input=self.dir, **args)

        except CalledModuleError as e:
            pass

    def print_products(self):
        for f in self.files:
            sys.stdout.write('Detected File <{0}> {1}'.format(str(f), os.linesep))

    # ------------------------------------------------------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------------------------------------------------------
    def __filter(self, filter_p):
        pattern = re.compile(filter_p)
        files = []
        for rec in os.walk(self.dir):
            if not rec[-1]:
                continue

            match = filter(pattern.match, rec[-1])
            if match is None:
                continue

            for f in match:
                if f.endswith(self.extension):
                    files.append(os.path.join(rec[0], f))

        return files


def main():
    dir = options['dir']
    outdir = options['outdir']
    shapefile = options['shapefile']
    t_srs = options['epsg']
    tr = options['resolution_value']
    scaling = options['scaling']
    geocoding_type = options['geocoding_type']
    polarizations = options['polarizations']
    offset = options['offset']
    externalDEMFile = options['external_dem_file']
    externalDEMNoDataValue = options['external_dem_nan']

    if options['pattern'] == '':
        pattern = None
    else:
        pattern = options['pattern']

    if shapefile is '':
        shapefile = None

    if outdir is '':
        outdir = os.path.join(os.path.dirname(dir), 'results')

    if t_srs is '':
        t_srs = 4326
    else:
        t_srs = int(t_srs)

    if tr is '':
        tr = 20

    if geocoding_type is 'Cross-Correlation':
        geocoding_type = 'SAR simulation cross correlation'

    if polarizations is 'all':
        pass
    elif polarizations is '':
        polarizations = 'all'
    else:
        polarizations = [polarizations]

    if offset is '':
        offset = None
    else:
        offset_list = offset.split(',')
        offset_list = [int(item) for item in offset_list]
        offset = tuple(offset_list)

    if externalDEMFile is '':
        externalDEMFile = None

    if externalDEMNoDataValue is '':
        externalDEMNoDataValue = None
    else:
        externalDEMNoDataValue = int(externalDEMNoDataValue)

    pp_geocode = Geocode(dir=dir, outdir=outdir, pattern=pattern, t_srs=t_srs, tr=tr, polarizations=polarizations,
                         shapefile=shapefile, scaling=scaling, geocoding_type=geocoding_type,
                         removeS1BoderNoise=flags['r'], offset=offset, externalDEMFile=externalDEMFile,
                         externalDEMNoDataValue=externalDEMNoDataValue, externalDEMApplyEGM=flags['e'],
                         test=flags['t'], verbose=flags['p'])

    pp_geocode.geocode()

    if flags['i']:
        pp_geocode.import_products(pattern=options['pattern'], f=flags['f'], l=flags['l'],
                                   p=flags['p'])

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    sys.exit(main())
