#!/usr/bin/env python

############################################################################
#
# MODULE:       c.database
# AUTHOR(S):    Ismail Baris
# PURPOSE:      Create a GRASS GIS Database and a Mapset.
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
#% key: mapset
#% type: string
#% multiple: no
#% required: yes
#% description: Name of the desired mapset:
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
"""

import os
import re
import subprocess
import sys

import grass.script as gs


class Database(object):
    def __init__(self, dir, mapset, t_srs=None, t_srs_from_file=None, launch=False):
        """
        Create a GRASS GIS Database and a Mapset.

        Parameters
        ----------
        dir : str
            Directory where the scenes are.
        mapname : str
            Mapname where the scenes where imported.
        t_srs : int, optional
            A EPSG Code for georeferencing.
        t_srs_from_file : str
            If t_srs is not used, a georeferenced file can be here uploaded.
        launch : bool
            If True, GRASS GIS will start with the new created mapset.
        """
        # Define GRASS GIS Versions ------------------------------------------------------------------------------------
        self.candidates = ['grass70', 'grass72', 'grass74']

        # Check Georeference -------------------------------------------------------------------------------------------
        if t_srs is None and t_srs_from_file is None:
            raise ValueError("A EPSG code (t_srs) or a geocoded file (t_srs_from_file) must be defined.")

        elif t_srs is not None and t_srs_from_file is not None:
            raise ValueError("Parameter t_srs AND A t_srs_from_file are defined. EPSG code OR a geocoded "
                             "file must be defined.")
        else:
            if t_srs is not None:
                self.t_srs = int(t_srs)
            else:
                self.t_srs = None

            if t_srs_from_file is not None:
                if not os.path.exists(t_srs_from_file):
                    raise ValueError("File <{0}> does not exist".format(t_srs_from_file))

                else:
                    self.t_srs_from_file = t_srs_from_file

            else:
                self.t_srs_from_file = None

        # Check Input Directory ----------------------------------------------------------------------------------------
        if not os.path.exists(dir):
            raise ValueError("Path <{0}> does not exist").format(dir)
        else:
            self.mapset = mapset
            self.dir = os.path.join(dir, self.mapset)

        # Self Definitions ---------------------------------------------------------------------------------------------
        self.launch = launch

    # ------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------------------------------------------------------
    def create_database(self):
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

        print("Mapset <{0}> created in database <{1}>".format(self.mapset, self.dir))

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
                startcmd = [grass_version, '-e', '-c', self.t_srs_from_file, self.dir]
            else:
                startcmd = [grass_version, '-e', '-c', self.t_srs_from_file, self.dir]

        return startcmd


def main():
    if options['t_srs_file'] == '':
        t_srs_file = None
    else:
        t_srs_file = options['t_srs_file']

    if options['t_srs'] == '':
        t_srs = None
    else:
        t_srs = options['t_srs']

    if flags['l']:
        launch = True
    else:
        launch = False

    creator = Database(dir=options['db_dir'], mapset=options['mapset'], t_srs_from_file=t_srs_file, t_srs=t_srs,
                       launch=launch)

    creator.create_database()

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    sys.exit(main())
