#!/usr/bin/env python

############################################################################
#
# MODULE:       g.database
# AUTHOR(S):    Ismail Baris
# PURPOSE:      Create a GRASS GIS Database.
#
# COPYRIGHT:    (C) Ismail Baris and Nils von Norsinski
#
#               This program is free software under the GNU General
#               Public License (>=v2). Read the file COPYING that
#               comes with GRASS for details.
#
#############################################################################


#%module
#% description: Create a GRASS GIS Database.
#% keyword: auxiliary
#% keyword: database
#% keyword: create
#%end

# Input Section --------------------------------------------------------------------------------------------------------
#%option G_OPT_M_DIR
#% key: db_dir
#% multiple: no
#% required: no
#% description: Select a directory where the database should be created:
#%guisection: Input
#%end

#%option
#% key: db_name
#% type: string
#% multiple: no
#% required: yes
#% description: Name of the desired database:
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
#% type: integer
#% required: no
#% multiple: no
#% description: Using a EPSG-Code:
#% guisection: Input
#%end

# Optional Section -----------------------------------------------------------------------------------------------------
#%flag
#% key: l
#% description: Launch mapset with GRASS GIS
#% guisection: Optional
#%end


import os
import re
import subprocess
import sys

try:
    import grass.script as gs
except ImportError:
    raise ImportError("You have to install GRASS GIS to run this program.")


class Database(object):
    """
    Create a GRASS GIS Database.

    Create a new location, including it's default PERMANENT mapset, with or
    without entering the new location.

    Parameters
    ----------
    db_dir : str
        Location of GRASS GIS database
    db_name : str
        Name of the database.
    t_srs : int, optional
        A EPSG Code for georeferencing purposes.
    t_srs_file : str, optional
        If t_srs is not used, a georeferenced file can be here uploaded.
    launch : bool, optional
        If True, GRASS GIS will start with the new created mapset.

    Attributes
    ----------
    db_dir : str
    db_name : str
    t_srs : str or NoneType
    t_srs_file : str or NoneType
    launch : bool

    Methods
    -------
    create_database()
        Create a GRASS GIS Database.

    Examples
    --------
    The general usage is
    ::
        $ g.database [-l] db_dir=string db_name=string [t_srs=integer] [t_srs_file=string] [--verbose] [--quiet]


    Create a new location, including it's default PERMANENT mapset, without entering the new location using
    a EPSG code::
        $ g.database db_dir=/home/user/grassdata db_name=germany t_srs=32630


    Create a new location, including it's default PERMANENT mapset, without entering the new location using
    a georeferenced raster file::
        $ g.database db_dir=/home/user/grassdata db_name=germany t_srs_file=myFile.tiff


    Create new mapset within the new location and launch GRASS GIS within that mapset
    ::
        $ g.database -l db_dir=/home/user/grassdata db_name=germany t_srs=32630

    Notes
    -----
    It is mandatory that t_srs OR t_srs_file is set.

    This class trys to find `['grass70', 'grass71', 'grass72', 'grass73', 'grass74']` commands. This list can
    easily be extended for other versions of GRASS GIS.

    **Flags:**
        * l : Launch mapset with GRASS GIS.
    """

    def __init__(self, db_dir, db_name, t_srs=None, t_srs_file=None, launch=False):

        # Define GRASS GIS Versions ------------------------------------------------------------------------------------
        self.candidates = ['grass70', 'grass71', 'grass72', 'grass73', 'grass74']

        # Check Georeference -------------------------------------------------------------------------------------------
        if t_srs is None and t_srs_file is None:
            raise ValueError("A EPSG code (t_srs) or a geocoded file (t_srs_file) must be defined.")

        elif t_srs is not None and t_srs_file is not None:
            raise ValueError("Parameter t_srs AND A t_srs_file are defined. EPSG code OR a geocoded "
                             "file must be defined.")
        else:
            if t_srs is not None:
                self.t_srs = int(t_srs)
            else:
                self.t_srs = None

            if t_srs_file is not None:
                if not os.path.exists(t_srs_file):
                    raise ValueError("File <{0}> does not exist".format(t_srs_file))

                else:
                    self.t_srs_file = t_srs_file

            else:
                self.t_srs_file = None

        # Check Input Directory ----------------------------------------------------------------------------------------
        self.db_name = db_name
        self.dir = os.path.join(db_dir, self.db_name)

        # Self Definitions ---------------------------------------------------------------------------------------------
        self.launch = launch

    # ------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------------------------------------------------------
    def create_database(self):
        """
        Create a GRASS GIS Database.

        Returns
        -------
        None
        """
        for grass_version in self.candidates:
            try:
                startcmd = self.__build_start_command(grass_version)
                p = subprocess.Popen(startcmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()

                if p.returncode != 0:
                    print(out + err)
                    print('failed: {}'.format(dir))
                    err_match = re.search('Error: (.*)\n', out + err)
                    errmessage = err_match.group(1) if err_match else err
                    raise RuntimeError(errmessage)

            except OSError:
                pass
            else:
                break

        print("Database <{0}> created in database <{1}>".format(self.db_name, self.dir))

    # ------------------------------------------------------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------------------------------------------------------
    def __build_start_command(self, grass_version):
        if self.t_srs is not None:
            EPSG = self.t_srs

            if self.launch:
                startcmd = [grass_version, '-c', 'EPSG:' + str(EPSG), self.dir]
            else:
                startcmd = [grass_version, '-e', '-c', 'EPSG:' + str(EPSG), self.dir]

        else:
            if self.launch:
                startcmd = [grass_version, '-c', self.t_srs_file, self.dir]
            else:
                startcmd = [grass_version, '-e', '-c', self.t_srs_file, self.dir]

        return startcmd


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
    creator = Database(db_dir=options['db_dir'], db_name=options['db_name'],
                       t_srs_file=options['t_srs_file'], t_srs=options['t_srs'],
                       launch=flags['l'])

    creator.create_database()

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    options = change_dict_value(options, '', None)

    sys.exit(main())
