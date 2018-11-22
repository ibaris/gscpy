#!/usr/bin/env python

############################################################################
#
# MODULE:       g.database
# AUTHOR(S):    Ismail Baris
# PURPOSE:      Create a mapset in aGRASS GIS Database.
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
#% description: Create a mapset in aGRASS GIS Database.
#% keyword: auxiliary
#% keyword: database
#% keyword: create
#%end

# Input Section --------------------------------------------------------------------------------------------------------
#%option
#% key: mapset
#% type: string
#% multiple: no
#% required: yes
#% description: Name of mapset:
#%guisection: Input
#%end

#%option
#% key: location
#% type: string
#% multiple: no
#% required: no
#% description: Location name (not location path):
#%guisection: Input
#%end

#%option G_OPT_M_DIR
#% key: dbase
#% multiple: no
#% required: no
#% description: GRASS GIS database directory:
#%guisection: Input
#%end
"""

import sys

try:
    import grass.script as gs
    from grass.exceptions import CalledModuleError
except ImportError:
    raise ImportError("You must installed GRASS GIS to run this program.")


class Mapset(object):
    def __init__(self, mapset, dbase=None, location=None):
        """
        Create a GRASS GIS Database.

        Parameters
        ----------
        dbase : str
            Location of GRASS GIS database
        mapset : str
            Name of the mapset that will be created.
        """

        # Check Input Directory ----------------------------------------------------------------------------------------

        self.mapset = mapset
        self.dbase = dbase
        self.location = location

    # ------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------------------------------------------------------
    def create_mapset(self, flag='c'):
        self.__run_command(flag)

        print("Mapset <{0}> created.".format(self.mapset))

    # ------------------------------------------------------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------------------------------------------------------
    def __run_command(self, flag='c'):
        module = 'g.mapset'
        args = {'mapset': self.mapset}

        if self.dbase is not None:
            args['dbase'] = self.dbase

        if self.location is not None:
            args['location'] = self.location

        try:
            gs.run_command(module, flags=flag, **args)

        except CalledModuleError as e:
            pass


def main():
    if options['location'] == '':
        location = None
    else:
        location = options['location']

    if options['dbase'] == '':
        dbase = None
    else:
        dbase = options['dbase']

    flag = 'c'

    creator = Mapset(mapset=options['mapset'], dbase=dbase, location=location)

    creator.create_mapset(flag)

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    sys.exit(main())
