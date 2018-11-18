#!/usr/bin/env python

#%module
#% description: Download Sentinel 1 Data
#% keyword: download
#%end

#%option G_OPT_F_INPUT
#% key: timestart
#% description: Starting time of observation period (YYYY-MM-DD).
#%end

#%option G_OPT_F_INPUT
#% key: timend
#% description: End time of observation period (YYYY-MM-DD).
#%end

#%option G_OPT_F_INPUT
#% key: orbitnumber
#% required: no
#% description: Choose the orbitnumber.
#%end

#%option
#% key: polarisationmode
#% required: no
#% options: HH, VV, HV, VH, HH HV, VV VH
#% answer: HH
#% description: Choose the polarisationmode.
#%end

#%option
#% key: producttype
#% options: SLC, GRD, OCN
#% answer: SLC
#% description: Choose the producttype.
#%end

#%option
#% options: SM, IW, EW, WV
#% answer: SM
#% key: sensoroperationalmode
#% required: no
#% description: Choose the sensoroperationalmode.
#%end

#%option
#% key: swathidentifier
#% options: S1, S2, S3, S4, S5, S6, IW, IW1, IW2, IW3, EW, EW1, EW2, EW3, EW4, EW5
#% answer: S1
#% required: no
#% description: Choose the swathidentifier.
#%end

#%option G_OPT_F_INPUT
#% key: region
#% type: string
#% description: Choose geojson file to define the observation area.

import sys

import grass.script as gscript


def main():
    options, flags = gscript.parser()
    timestart = options['timestart']
    timeend = options['timend']
    orbitnumber = options['orbitnumber']
    polarisationmode = options['polarisationmode']
    producttype = options['producttype']
    sensoroperationalmode = options['sensoroperationalmode']
    swathidentifier = options['swathidentifier']

    region = options['region']
    print(region)


    return 0


if __name__ == "__main__":
    sys.exit(main())
