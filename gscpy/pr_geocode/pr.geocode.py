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
#%option G_OPT_F_INPUT
#% key: infile
#% multiple: no
#% description: The SAR scene to be processed:
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
#% type: int
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
"""

import os
import sys

import grass.script as gscript
from pyroSAR.snap.util import geocode


def main():
    options, flags = gscript.parser()

    infile = options['infile']
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

    if shapefile is '':
        shapefile = None

    if outdir is '':
        outdir = os.path.dirname(infile)

    if t_srs is '':
        t_srs = 4326

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

    geocode(infile, outdir, t_srs=t_srs, tr=tr, polarizations=polarizations, shapefile=shapefile, scaling=scaling,
            geocoding_type=geocoding_type, removeS1BoderNoise=removeS1BoderNoise, offset=offset,
            externalDEMFile=externalDEMFile, externalDEMNoDataValue=externalDEMNoDataValue,
            externalDEMApplyEGM=externalDEMApplyEGM, test=test)

    return 0


if __name__ == "__main__":
    sys.exit(main())
