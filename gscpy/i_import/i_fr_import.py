#!/usr/bin/env python

############################################################################
#
# MODULE:      i.fr.import
# AUTHOR(S):   Ismail Baris
# PURPOSE:     Import pyroSAR dataset in a directory based on their metadata.
#
# COPYRIGHT:   (C) Ismail Baris and Nils von Norsinski
#
#              This program is free software under the GNU General Public
#              License (>=v2). Read the file COPYING that comes with GRASS
#              for details.
#
#############################################################################


#%Module
#% description: Import pyroSAR datasets in a directory based on their metadata
#% keyword: imagery
#% keyword: satellite
#% keyword: pyrosar
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
#% key: sensor
#% required: no
#% type: string
#% multiple: yes
#% description: Sensor.
#% guisection: Filter
#%end

#%option
#% key: acquisition_mode
#% required: no
#% type: string
#% multiple: yes
#% description: Acquisition Mode.
#% guisection: Filter
#%end

#%option
#% key: polarization
#% required: no
#% type: string
#% multiple: yes
#% description: Polarization.
#% guisection: Filter
#%end

#%option
#% key: product
#% required: no
#% type: string
#% multiple: yes
#% description: Product.
#% guisection: Filter
#%end

#%option
#% key: projection
#% required: no
#% type: string
#% multiple: yes
#% description: Projection.
#% guisection: Filter
#%end

#%option
#% key: orbit
#% required: no
#% type: string
#% multiple: yes
#% description: Orbit.
#% guisection: Filter
#%end

#%option
#% key: spacing
#% required: no
#% type: string
#% multiple: yes
#% description: Spacing.
#% guisection: Filter
#%end

#%option
#% key: sample
#% required: no
#% type: string
#% multiple: yes
#% description: Sample.
#% guisection: Filter
#%end

#%option
#% key: lines
#% required: no
#% type: string
#% multiple: yes
#% description: Lines.
#% guisection: Filter
#%end

# Date Section -----------------------------------------------------------------------------------------------------
#%option
#% key: start
#% required: no
#% type: string
#% multiple: no
#% description: Start Time.
#% guisection: Date
#%end

#%option
#% key: stop
#% required: no
#% type: string
#% multiple: no
#% description: End Time.
#% guisection: Date
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
#% key: e
#% description: Recursive
#% guisection: Optional
#%end

#%flag
#% key: p
#% description: Print the detected files and exit.
#% guisection: Optional
#%end

#%flag
#% key: r
#% description: Reproject raster data (using r.import if needed).
#% guisection: Optional
#%end

#%flag
#% key: l
#% description: Link raster data instead of importing.
#% guisection: Optional
#%end


import os
import sys

from pyroSAR.ancillary import find_datasets

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

__LOCAL__ = ['sensor', 'projection', 'orbit', 'polarization', 'acquisition_mode',
             'start', 'stop', 'product', 'spacing', 'samples', 'lines']


class FinderImport(object):
    """
    Import pyroSAR dataset in a directory based on their metadata.

    Parameters
    ----------
    input_dir : str
        The directory where the files are located.
    recursive : bool, optional
        Recursive search. Default is False.
    sensor : str or tuple, optional
        Sensor.
    projection : str or tuple, optional
        Projection.
    orbit : str or tuple, optional
        Orbit.
    polarization : str or tuple, optional
        Polarization.
    acquisition_mode : str or tuple, optional
        Acquisition_mode.
    start : str or tuple, optional
        Start.
    stop : str or tuple, optional
        Stop.
    product : str or tuple, optional
        Product.
    spacing : str or tuple, optional
        Spacing.
    sample : str or tuple, optional
        Sample.
    lines : str or tuple, optional
        Lines.

    Attributes
    ----------
    input_dir : str
    recursive : bool
    kwargs : dict
        Selected attributs (sensor, polarization etc.) in a dictionary.
    files : list
        All detected files.

    Methods
    -------
    find_products()
        Find all files that matches the input attributes.
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
        $ i.fr.import [-r -l -c -p -e] input_dir=string [*attributes=string] [mapset=string] [dbase=string] [location=string] [--verbose] [--quiet]


    For *attributes the following parameters can be used
    ::
        >>> ['sensor', 'projection', 'orbit', 'polarization', 'acquisition_mode', 'start', 'stop', 'product', 'spacing', 'samples', 'lines']


    Import Sentinel 1A files with polarization VV and VH from a directory in current mapset and reproject it
    ::
        $ i.fr.import -r input_dir=/home/user/data sensor=SA1 polarization=VV, VH


    Import Sentinel 1A and 1B files with polarization VV from a directory in a new mapset and reproject it
    ::
        $ i.fr.import -c -r input_dir=/home/user/data sensor=S1A, S1B polarization=VV mapset=Goettingen

    Notes
    -----
    **Flags:**
        * r : Reproject raster data (using r.import if needed).
        * l : Link raster data instead of importing.
        * c : Create a new mapset.
        * p : Print the detected files and exit.
        * e : Recursive search.

    """

    def __init__(self, input_dir, recursive=False, sensor=None, projection=None, orbit=None, polarization=None,
                 acquisition_mode=None, start=None, stop=None, product=None, spacing=None, sample=None,
                 lines=None):

        # Initialize Directory -----------------------------------------------------------------------------------------
        self.input_dir = input_dir
        self.recursive = recursive

        # Initialize kwargs --------------------------------------------------------------------------------------------
        input_parameter = [sensor, projection, orbit, polarization, acquisition_mode, start, stop, product, spacing,
                           sample, lines]
        self.kwargs = {}

        for i, item in enumerate(input_parameter):
            if item is not None:
                self.kwargs[__LOCAL__[i]] = item

        # Select Files -------------------------------------------------------------------------------------------------
        self.files = self.find_products()

    # ------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------------------------------------------------------
    def find_products(self):
        """
        Find all files that matches the input attributes.
        Returns
        -------
        list
        """
        return find_datasets(self.input_dir, self.recursive, **self.kwargs)

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
        module = 'g.mapset'
        gs.run_command(module, flags='c', mapset=mapset, dbase=dbase, location=location)

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

    def __import_file(self, filename, module, args, mapname=None):
        if mapname is None:
            mapname = os.path.splitext(os.path.basename(filename))[0]
        else:
            pass

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


def tuple_multi_string(dictionary, sep=','):
    """
    Convert values like 'a, b' to ('a', 'b').

    Parameters
    ----------
    dictionary : dict
        Input dictionary.
    sep : str
        Seperator

    Returns
    -------
    dict
    """
    for key, value in dictionary.items():
        value_split = value.split(sep)

        if len(value_split) == 1 or len(value_split) == 0:
            pass
        else:
            dictionary[key] = tuple(value_split)

    return dictionary


def main():
    importer = FinderImport(options['input_dir'], recursive=flags['e'], sensor=options['sensor'],
                            projection=options['projection'], orbit=options['orbit'],
                            polarization=options['polarization'],
                            acquisition_mode=options['acquisition_mode'], start=options['start'], stop=options['stop'],
                            product=options['product'], spacing=options['spacing'], sample=options['sample'],
                            lines=options['lines'])


    if flags['p']:
        importer.print_products()
        return 0

    if flags['c']:
        if options['mapset'] is None:
            raise ValueError("Please define a mapset.")
        else:
            importer.create_mapset(mapset=options['mapset'], dbase=options['dbase'], location=options['location'])

    importer.import_products(flags['r'], flags['l'])

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    options = tuple_multi_string(options)
    options = change_dict_value(options, '', None)
    sys.exit(main())
