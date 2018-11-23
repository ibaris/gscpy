#!/usr/bin/env python

############################################################################
#
# MODULE:      i.dr.import
# AUTHOR(S):   Ismail Baris
# PURPOSE:     Import data into a mapset from a file with considering a certain pattern.
#
# COPYRIGHT:   (C) Ismail Baris and Nils von Norsinski
#
#              This program is free software under the GNU General Public
#              License (>=v2). Read the file COPYING that comes with GRASS
#              for details.
#
#############################################################################


#%Module
#% description: Import data into a mapset from a file with considering a certain pattern.
#% keyword: imagery
#% keyword: satellite
#% keyword: auxiliary
#% keyword: import
#%end

# Input Section --------------------------------------------------------------------------------------------------------
#%option G_OPT_M_DIR
#% key: input_dir
#% description: The directory where the files are located.
#% required: yes
#%guisection: Input
#%end

# Filter Section -------------------------------------------------------------------------------------------------------
#%option
#% key: pattern
#% description: The pattern of file names.
#% guisection: Filter
#%end

#%option
#% key: extension
#% type: string
#% required: no
#% multiple: no
#% answer: .tif
#% options: .tif, .tiff, .img
#% description: Which extension should be considered?
#% guisection: Filter
#%end

# Settings Section -----------------------------------------------------------------------------------------------------
#%flag
#% key: r
#% description: Reproject raster data (using r.import if needed).
#% guisection: Settings
#%end

#%flag
#% key: l
#% description: Link raster data instead of importing.
#% guisection: Settings
#%end

# Mapset Section -------------------------------------------------------------------------------------------------------
#%flag
#% key: c
#% description: Create a new mapset.
#% guisection: Mapset
#%end

#%option
#% key: mapset
#% required: no
#% type: string
#% multiple: no
#% description: Name of mapset.
#%guisection: Mapset
#%end

#%option
#% key: location
#% type: string
#% multiple: no
#% required: no
#% description: Location name (not location path).
#%guisection: Mapset
#%end

#%option G_OPT_M_DIR
#% key: dbase
#% multiple: no
#% required: no
#% description: GRASS GIS database directory.
#%guisection: Mapset
#%end

# Optional Section -----------------------------------------------------------------------------------------------------
#%flag
#% key: p
#% description: Print the detected files and exit.
#% guisection: Optional
#%end


import os
import re
import sys

try:
    import grass.script as gs
    from grass.exceptions import CalledModuleError
except ImportError:
    raise ImportError("You must installed GRASS GIS to run this program.")

try:
    from osgeo import gdal, osr
except ImportError as e:
    gs.fatal(_("Flag -r requires GDAL library: {}").format(e))

    raise ImportError("You must installed GRASS GIS to run this program.")


class DirImport(object):
    """
    Import data into a mapset from a file with considering a certain pattern.

    Parameters
    ----------
    input_dir : str
        The directory where the files are located.
    pattern : str, optional
        The pattern of file names. If not specified all files with selected extension will be imported.
    extension : {'ENVI', 'GEOTIFF'}, optional
        Which extensions should be recognized? Default is 'GEOTIFF'

    Attributes
    ----------
    input_dir : str
    extension : str
    filter_p : str
        Combines pattern and extension.
    files : list
        All detected files.

    Methods
    -------
    import_products(reproject=False, link=False)
        Import detected files.
    create_mapset(mapset, dbase=None, location=None)
        Create a new mapset.
    print_products()
        Print all detected files.

    Examples
    --------
    The general usage is
    ::
        $ i.dr.import [-r -l -c -p] input_dir=string [pattern=string] [extension=string] [mapset=string] [dbase=string] [location=string] [--verbose] [--quiet]


    Import files that starts with 'S1' from a directory in current mapset and reproject it
    ::
        $ i.dr.import -r input_dir=/home/user/data pattern=S1.*


    Import files that starts with 'S1' from a directory in a new mapset and reproject it
    ::
        $ i.dr.import -c -r input_dir=/home/user/data pattern=S1.* mapset=Goettingen

    Notes
    -----
    Note, it is important for the parameter `pattern`  that the asterisk('*') contains a dot (see examples).

    **Flags:**
        * r : Reproject raster data (using r.import if needed).
        * l : Link raster data instead of importing.
        * c : Create a new mapset.
        * p : Print the detected files and exit.

    """
    def __init__(self, input_dir, pattern=None, extension=None):
        # Initialize Directory -----------------------------------------------------------------------------------------
        self._dir_list = []

        if not os.path.exists(input_dir):
            gs.fatal(_('Input directory <{0}> not exists').format(input_dir))
        else:
            self.input_dir = input_dir

        # Create Pattern and find files --------------------------------------------------------------------------------
        if extension is not None:
            self.extension = extension
        else:
            self.extension = '.tif'

        if pattern is not None:
            filter_p = pattern + self.extension
        else:
            filter_p = '.*' + self.extension

        self.filter_p = filter_p

        gs.debug('Filter: {}'.format(filter_p), 1)
        self.files = self.__filter(filter_p)

        if self.files is []:
            gs.message(_('No files detected. Note, that must be a point for * like: pattern = str.* '))
            return

    # ------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------------------------------------------------------
    def import_products(self, reproject=False, link=False):
        """
        Import detected files.

        Parameters
        ----------
        reproject : bool
            Reproject raster data (using r.import if needed).
        link : bool
            Link raster data instead of importing.

        Returns
        -------
        None
        """
        args = {}
        if link:
            module = 'r.external'
        else:
            if reproject:
                module = 'r.import'
                args['resample'] = 'bilinear'
                args['resolution'] = 'value'
            else:
                module = 'r.in.gdal'

            for f in self.files:
                if link or (not link and not reproject):
                    if not self.__check_projection(f):
                        gs.fatal(_('Projection of dataset does not appear to match current location. '
                                   'Force reprojecting dataset by -r flag.'))

                self.__import_file(f, module, args)

    def create_mapset(self, mapset, dbase=None, location=None):
        """
        Create a new mapset calling the module `g.c.mapset`.

        Parameters
        ----------
        mapset : str
            Name of mapset.
        dbase : str, optional
            Location of GRASS GIS database
        mapset : str, optional
            Name of the mapset that will be created.

        Returns
        -------
        None
        """
        module = 'g.c.mapset'
        gs.run_command(module, mapset=mapset, dbase=dbase, location=location)

    def print_products(self):
        """
        Print all detected files.

        Returns
        -------
        None
        """
        for f in self.files:
            sys.stdout.write(
                'Detected File <{0}> {1} (EPSG: {2}){3}'.format(str(f), '1' if self.__check_projection(f) else '0',
                                                                str(self.__raster_epsg(f)), os.linesep))

    # ------------------------------------------------------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------------------------------------------------------
    def __filter(self, filter_p):
        pattern = re.compile(filter_p)
        files = []
        for rec in os.walk(self.input_dir):
            if not rec[-1]:
                continue

            match = filter(pattern.match, rec[-1])
            if match is None:
                continue

            for f in match:

                if f.endswith(self.extension):
                    files.append(os.path.join(rec[0], f))

        return files

    def __check_projection(self, filename):
        try:
            with open(os.devnull) as null:
                gs.run_command('r.in.gdal', flags='j',
                               input=filename, quiet=True)
        except CalledModuleError as e:
            return False

        return True

    def __raster_resolution(self, filename):
        dsn = gdal.Open(filename)
        trans = dsn.GetGeoTransform()

        ret = int(trans[1])
        dsn = None

        return ret

    def __raster_epsg(self, filename):
        dsn = gdal.Open(filename)

        srs = osr.SpatialReference()
        srs.ImportFromWkt(dsn.GetProjectionRef())

        ret = srs.GetAuthorityCode(None)
        dsn = None

        return ret

    def __import_file(self, filename, module, args):
        mapname = os.path.splitext(os.path.basename(filename))[0]

        gs.message(_('Processing <{}>...').format(mapname))

        if module == 'r.import':
            args['resolution_value'] = self.__raster_resolution(filename)

        try:
            gs.run_command(module, input=filename, output=mapname, **args)
            gs.raster_history(mapname)

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
    importer = DirImport(options['input_dir'], pattern=options['pattern'], extension=options['extension'])

    if flags['p']:
        importer.print_products()
        return 0

    if flags['c']:
        if options['mapset'] == '':
            raise ValueError("Please define a mapset.")
        else:
            importer.create_mapset(mapset=options['mapset'], dbase=options['dbase'], location=options['location'])

    importer.import_products(flags['r'], flags['l'])

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    options = change_dict_value(options, '', None)

    sys.exit(main())
