#!/usr/bin/env python

############################################################################
#
# MODULE:       g.c.database
# AUTHOR(S):    Ismail Baris
# PURPOSE:      Create a mapset in a GRASS GIS Database.
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
#% keyword: mapset
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
        Create a mapset in a GRASS GIS Database if it is not existent. This will changes the current working MAPSET,
        LOCATION, or GISDBASE. This is a fairly radical maneuver to run mid-session, take care when running the GUI
        at the same time.

        In GRASS GIS their is a similar function (`g.mapset`). This function shortens the flags and creates directly
        a new mapset if it is not existent.

        Parameters
        ----------
        mapset : str
            Name of mapset.
        dbase : str, optional
            Location of GRASS GIS database
        mapset : str, optional
            Name of the mapset that will be created.

        Attributes
        ----------
        mapset : str
        dbase : str
        location : str

        Methods
        -------
        create_mapset()
            Create a mapset in a GRASS GIS Database if it is not existent.

        Examples
        --------
        The general usage is::
            $ g.c.mapset [] mapset=string [dbase=string] [location=string] [--verbose] [--quiet]

        Creation of a mapset within a GRASS GIS session::
            $ g.c.mapset mapset=Goettingen


        Creation of a mapset within another GRASS GIS database::
            $ g.c.mapset mapset=Goettingen dbase=/home/user/grassdata/germany


        By default, the shell continues to use the history for the old mapset. To change this behaviour the history
        can be switched to record in the new mapset's history file as follows::
            $ g.c.mapset mapset=Goettingen
            history -w
            history -r /"$GISDBASE/$LOCATION/$MAPSET"/.bash_history
            HISTFILE=/"$GISDBASE/$LOCATION/$MAPSET"/.bash_history

        Notes
        -----
        By default, the shell continues to use the history for the old mapset. To change this behaviour the history
        look at the examples.
        """

        # Self Definitions ---------------------------------------------------------------------------------------------
        self.mapset = mapset
        self.dbase = dbase
        self.location = location

    # ------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------------------------------------------------------
    def create_mapset(self):
        """
        Create a mapset in a GRASS GIS Database if it is not existent.

        Returns
        -------
        None
        """
        self.__run_command()

        print("Mapset <{0}> created.".format(self.mapset))

        return 0

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
    creator = Mapset(mapset=options['mapset'], dbase=options['dbase'], location=options['location'])
    creator.create_mapset()

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    options = change_dict_value(options, '', None)
    sys.exit(main())
