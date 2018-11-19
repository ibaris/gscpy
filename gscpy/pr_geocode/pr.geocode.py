#!/usr/bin/env python

############################################################################
#
# MODULE:       pr.geocode
#
# AUTHOR(S):    Ismail Baris
#
# PURPOSE:      Wrapper function for geocoding SAR images using ESA SNAP.
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
#% description: Name for input directory where Sentinel data lives:
#%guisection: Input
#%end

#%option G_OPT_F_INPUT
#% key: shapefile
#% required: no
#% multiple: no
#% description: A vector geometry for subsetting the SAR scene to a test site:
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
#%option G_OPT_F_INPUT
#% key: outdir
#% required: no
#% multiple: no
#% description: The directory to write the final files to:
#%guisection: Input
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

# Filter Section -------------------------------------------------------------------------------------------------------
#%option
#% key: pattern
#% description: File name pattern to import
#% guisection: Filter
#%end

# Optional Section -----------------------------------------------------------------------------------------------------
#%option
#% key: polarizations
#% type: string
#% required: no
#% multiple: yes
#% description: The polarizations to be processed (Default is 'all'):
#% guisection: Optional
#%end

#%option
#% key: remove_boder_noise
#% type: string
#% required: no
#% multiple: no
#% answer: True
#% options: True, False
#% description: Enables removal of S1 GRD border noise:
#% guisection: Optional
#%end

#%option
#% key: offset
#% type: integer
#% required: no
#% multiple: yes
#% description: Integers defining offsets for left, right, top and bottom in pixels, e.g. 100, 100, 0, 0:
#% guisection: Optional
#%end

#%option G_OPT_F_INPUT
#% key: external_dem_file
#% required: no
#% multiple: no
#% description: The absolute path to an external DEM file:
#%guisection: Optional
#%end

#%option
#% key: external_dem_nan
#% type: integer
#% required: no
#% multiple: no
#% description: The no data value of the external DEM:
#% guisection: Optional
#%end

#%option
#% key: external_dem_egm
#% type: string
#% required: no
#% multiple: no
#% answer: True
#% options: True, False
#% description: Apply Earth Gravitational Model to external DEM?:
#% guisection: Optional
#%end

#%option
#% key: test
#% type: string
#% required: no
#% multiple: no
#% answer: False
#% options: True, False
#% description: Write only the workflow in xml file:
#% guisection: Optional
#%end

# Print Section --------------------------------------------------------------------------------------------------------
#%flag
#% key: p
#% description: Print raster data to be imported and exit
#% guisection: Print
#%end
"""

import os
import sys
import re
import datetime as dt

import grass.script as gs
from pyroSAR.snap.util import geocode


class Geocode(object):
    def __init__(self, dir, outdir, pattern=None, t_srs=4326, tr=20, polarizations='all', shapefile=None, scaling='dB',
                 geocoding_type='Range-Doppler', removeS1BoderNoise=True, offset=None, externalDEMFile=None,
                 externalDEMNoDataValue=None, externalDEMApplyEGM=True, basename_extensions=None, test=False,
                 verbose=False):

        # Initialize DIRS ----------------------------------------------------------------------------------------------
        self._dir_list = []

        if not os.path.exists(dir):
            gs.fatal(_('Input directory <{}> not exists').format(dir))
        else:
            self.dir = dir

        if not os.path.exists(outdir):
            os.makedirs(outdir)
        else:
            self.outdir = dir

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
        for infile in self.files:
            if self.verbose:
                sys.stdout.write('Start Time: {0}'.format(dt.datetime.utcnow().__str__()))
                sys.stdout.write('Start Processing File: {0} {1}'.format(str(os.path.basename(infile)), os.linesep))

            geocode(infile, self.outdir, t_srs=self.t_srs, tr=self.tr, polarizations=self.polarizations,
                    shapefile=self.shapefile, scaling=self.scaling, geocoding_type=self.geocoding_type,
                    removeS1BoderNoise=self.removeS1BoderNoise, offset=self.offset,
                    externalDEMFile=self.externalDEMFile, externalDEMNoDataValue=self.externalDEMNoDataValue,
                    externalDEMApplyEGM=self.externalDEMApplyEGM, test=self.test)

            if self.verbose:
                sys.stdout.write('End Time: {0}'.format(dt.datetime.utcnow().__str__()))
                sys.stdout.flush()

    def print_products(self):
        for f in self.files:
            sys.stdout.write('{0} {1}'.format(str(f), os.linesep))

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
    options, flags = gs.parser()

    dir = options['dir']
    outdir = options['outdir']
    shapefile = options['shapefile']
    t_srs = options['epsg']
    tr = options['resolution_value']
    scaling = options['scaling']
    geocoding_type = options['geocoding_type']
    polarizations = options['polarizations']
    removeS1BoderNoise = options['remove_boder_noise']
    offset = options['offset']
    externalDEMFile = options['external_dem_file']
    externalDEMNoDataValue = options['external_dem_nan']
    externalDEMApplyEGM = options['external_dem_egm']
    test = options['test']

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

    if removeS1BoderNoise is 'True':
        removeS1BoderNoise = True
    else:
        removeS1BoderNoise = False

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

    if externalDEMApplyEGM is 'True':
        externalDEMApplyEGM = True
    else:
        externalDEMApplyEGM = False

    if test is 'True':
        test = True
    else:
        test = False

    if flags['p']:
        verbose = True
    else:
        verbose = False

    pp_geocode = Geocode(dir=dir, outdir=outdir, pattern=pattern, t_srs=t_srs, tr=tr, polarizations=polarizations,
                         shapefile=shapefile, scaling=scaling, geocoding_type=geocoding_type,
                         removeS1BoderNoise=removeS1BoderNoise, offset=offset, externalDEMFile=externalDEMFile,
                         externalDEMNoDataValue=externalDEMNoDataValue, externalDEMApplyEGM=externalDEMApplyEGM,
                         test=test, verbose=verbose)

    pp_geocode.geocode()

    return 0


if __name__ == "__main__":
    sys.exit(main())
