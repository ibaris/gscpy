#!/usr/bin/env python

############################################################################
#
# MODULE:       pp.geocode
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

# %module
# % description: Wrapper function for geocoding SAR images using ESA SNAP.
# % keyword: processing
# % keyword: sar
# % keyword: sentinel 1
# %end

# Input Section --------------------------------------------------------------------------------------------------------
# %option G_OPT_F_INPUT
# % key: infile
# % multiple: no
# % description: The SAR scene to be processed:
# %guisection: Input
# %end

# %option G_OPT_F_INPUT
# % key: shapefile
# % required: no
# % multiple: no
# % description: A vector geometry for subsetting the SAR scene to a test site:
# %guisection: Input
# %end

# %option
# % key: EPSG
# % type: int
# % required: no
# % multiple: no
# % description: A target geographic reference system in EPSG, (Default is 4326):
# %guisection: Input
# %end

# Output Section -------------------------------------------------------------------------------------------------------
# %option
# % key: resolution_value
# % type: double
# % required: no
# % multiple: no
# % description: Resolution of output raster map:
# % guisection: Output
# %end

# %option
# % key: scaling
# % type: string
# % required: no
# % multiple: no
# % answer: dB
# % options: dB,linear
# % description: Should the output be in linear or decibel scaling?:
# % guisection: Output
# %end

# %option
# % key: geocoding_type
# % type: string
# % required: no
# % multiple: no
# % answer: Range-Doppler
# % options: Range-Doppler, Cross-Correlation
# % description: The type of geocoding applied:
# % guisection: Output
# %end

# Optional Section -----------------------------------------------------------------------------------------------------
# %option
# % key: polarizations
# % type: string
# % required: no
# % multiple: yes
# % description: The polarizations to be processed (Default is 'all'):
# % guisection: Optional
# %end

# %option
# % key: removeS1BoderNoise
# % type: string
# % required: no
# % multiple: no
# % answer: True
# % options: True, False
# % description: Enables removal of S1 GRD border noise:
# % guisection: Optional
# %end

# %option
# % key: offset
# % type: integer
# % required: no
# % multiple: yes
# % description: Integers defining offsets for left, right, top and bottom in pixels, e.g. 100, 100, 0, 0:
# % guisection: Optional
# %end

# %option G_OPT_F_INPUT
# % key: externalDEMFile
# % required: no
# % multiple: no
# % description: The absolute path to an external DEM file:
# %guisection: Optional
# %end

# %option
# % key: externalDEMNoDataValue
# % type: integer
# % required: no
# % multiple: no
# % description: The no data value of the external DEM:
# % guisection: Optional
# %end

# %option
# % key: externalDEMApplyEGM
# % type: string
# % required: no
# % multiple: no
# % answer: True
# % options: True, False
# % description: Apply Earth Gravitational Model to external DEM?:
# % guisection: Optional
# %end

# %option
# % key: test
# % type: string
# % required: no
# % multiple: no
# % answer: True
# % options: True, False
# % description: If set to True the workflow xml file is only written and not executed:
# % guisection: Optional
# %end

import sys
from pyroSAR.snap.util import geocode
import grass.script as gscript


def main():
    options, flags = gscript.parser()
    infile = options['infile']
    shapefile = options['shapefile']
    t_srs = options['EPSG']
    tr = options['resolution_value']
    scaling = options['scaling']
    geocoding_type = options['geocoding_type']
    polarizations = options['polarizations']
    removeS1BoderNoise = options['removeS1BoderNoise']
    offset = options['offset']
    externalDEMFile = options['externalDEMFile']
    externalDEMNoDataValue = options['externalDEMNoDataValue']
    externalDEMApplyEGM = options['externalDEMApplyEGM']
    test = options['test']
    outdir = "/media/ibaris/Shared/Documents/GRASS_GIS_DB/GSCPY/PERMANENT"

    print(options)
    # geocode(infile, outdir, t_srs=t_srs, tr=tr, polarizations=polarizations, shapefile=shapefile, scaling=scaling,
    #         geocoding_type=geocoding_type, removeS1BoderNoise=removeS1BoderNoise, offset=offset,
    #         externalDEMFile=externalDEMFile, externalDEMNoDataValue=externalDEMNoDataValue,
    #         externalDEMApplyEGM=externalDEMApplyEGM, basename_extensions=None, test=test)

    return 0


if __name__ == "__main__":
    sys.exit(main())
