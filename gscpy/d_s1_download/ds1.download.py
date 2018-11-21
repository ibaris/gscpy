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
#% key: timend
#% description: End time of observation period (YYYY-MM-DD).
#% required: yes
#%guisection: Time
#%end

# Sensor Section -------------------------------------------------------------------------------------------------------
#%option
#% key: orbitnumber
#% required: no
#% description: Choose the orbitnumber.
#%guisection: Sensor
#%end

#%option
#% key: polarisationmode
#% required: no
#% options: all, HH, VV, HV, VH, HH HV, VV VH, HH VV HV VH HH HV VV VH
#% answer: all
#% description: Choose the polarisationmode.
#%guisection: Sensor
#%end

# Product Section ------------------------------------------------------------------------------------------------------
#%option
#% key: producttype
#% options: SLC, GRD, OCN
#% answer: SLC
#% description: Choose the producttype.
#%guisection: Product
#%end

#%option
#% options: SM, IW, EW, WV
#% answer: SM
#% key: sensoroperationalmode
#% required: no
#% description: Choose the sensoroperationalmode.
#%guisection: Product
#%end

#%option
#% key: swathidentifier
#% options: S1, S2, S3, S4, S5, S6, IW, IW1, IW2, IW3, EW, EW1, EW2, EW3, EW4, EW5
#% answer: S1
#% required: no
#% description: Choose the swathidentifier.
#%guisection: Product
#%end
"""

import os
import sys

try:
    import grass.script as gs
except ImportError:
    pass

def main():
    print options

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    sys.exit(main())
