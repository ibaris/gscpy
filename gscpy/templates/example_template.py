#!/usr/bin/env python

#%module
#% description: Download Sentinel 1 Data
#% keyword: download
#%end
#%option G_OPT_R_INPUT
#% key: timestart
#% description: Starting time of observation period (DD-MM-YYYY).
#%end
#%option G_OPT_R_INPUT
#% key: timend
#% description: End time of observation period (DD-MM-YYYY).
#%end
#%option G_OPT_R_INPUT
#% key: cloudcover
#% description: Set Cloudcover in Percentage .
#%end
#%option G_OPT_R_OUTPUT
#% key: region
#% description: Choose gjson file to define observation area.
#%end
#%option G_OPT_R_OUTPUT
#%end


import sys

import grass.script as gscript


def main():
    options, flags = gscript.parser()
    timestart = options['timestart']
    timeend = options['timend']
    cloudcover = options['cloudcover']

    region = region['region']
    # output = options['output']

    return 0


if __name__ == "__main__":
    sys.exit(main())
