#!/usr/bin/env python

############################################################################
#
# MODULE:      i.s1.import
# AUTHOR(S):   Ismail Baris
# PURPOSE:     Import pyroSAR datasets in a directory based on their metadata
#
# COPYRIGHT:   (C) Ismail Baris and Nils von Norsinski
#
#              This program is free software under the GNU General Public
#              License (>=v2). Read the file COPYING that comes with GRASS
#              for details.
#
#############################################################################

"""
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
#% description: Directory where the scenes are:
#% required: yes
#%guisection: Input
#%end

# Filter Section -------------------------------------------------------------------------------------------------------
#%option
#% key: sensor
#% required: no
#% type: string
#% multiple: yes
#% description: Sensor:
#% guisection: Filter
#%end

#%option
#% key: projection
#% required: no
#% type: string
#% multiple: yes
#% description: Projection:
#% guisection: Filter
#%end

#%option
#% key: orbit
#% required: no
#% type: string
#% multiple: yes
#% description: Orbit:
#% guisection: Filter
#%end

#%option
#% key: polarization
#% required: no
#% type: string
#% multiple: yes
#% description: Polarization:
#% guisection: Filter
#%end

#%option
#% key: acquisition_mode
#% required: no
#% type: string
#% multiple: yes
#% description: Acquisition Mode:
#% guisection: Filter
#%end

#%option
#% key: start
#% required: no
#% type: string
#% multiple: yes
#% description: Start:
#% guisection: Filter
#%end

#%option
#% key: stop
#% required: no
#% type: string
#% multiple: yes
#% description: Stop:
#% guisection: Filter
#%end

#%option
#% key: product
#% required: no
#% type: string
#% multiple: yes
#% description: Product:
#% guisection: Filter
#%end

#%option
#% key: spacing
#% required: no
#% type: string
#% multiple: yes
#% description: Spacing:
#% guisection: Filter
#%end

#%option
#% key: sample
#% required: no
#% type: string
#% multiple: yes
#% description: Sample:
#% guisection: Filter
#%end

#%option
#% key: lines
#% required: no
#% type: string
#% multiple: yes
#% description: Lines:
#% guisection: Filter
#%end

# Settings Section -----------------------------------------------------------------------------------------------------
#%flag
#% key: r
#% description: Reproject raster data using r.import if needed
#% guisection: Settings
#%end

#%flag
#% key: l
#% description: Link raster data instead of importing
#% guisection: Settings
#%end

# Mapset Section -------------------------------------------------------------------------------------------------------
#%flag
#% key: c
#% description: Create a new mapset
#% guisection: Mapset
#%end

#%option
#% key: mapset
#% required: no
#% type: string
#% multiple: no
#% description: Name of mapset:
#%guisection: Mapset
#%end

#%option
#% key: location
#% type: string
#% multiple: no
#% required: no
#% description: Location name (not location path):
#%guisection: Mapset
#%end

#%option G_OPT_M_DIR
#% key: dbase
#% multiple: no
#% required: no
#% description: GRASS GIS database directory:
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
#% description: Print raster data to be imported and exit
#% guisection: Optional
#%end
"""

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

__LOCAL__ = ['sensor', 'projection', 'orbit', 'polarizations', 'acquisition_mode',
             'start', 'stop', 'product', 'spacing', 'samples', 'lines']


class Finder(object):
    def __init__(self, input_dir, recursive=False, sensor=None, projection=None, orbit=None, polarization=None,
                 acquisition_mode=None, start=None, stop=None, product=None, spacing=None, sample=None,
                 lines=None):

        """
        Import pre-processed (pr.geocode) Sentinel 1 data into a mapset.

        Parameters
        ----------
        input_list : str
            A list with paths to files.
        """
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
        return find_datasets(self.input_dir, self.recursive, **self.kwargs)

    def import_products(self, reproject=False, link=False):
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

                if os.path.exists(f):
                    pass
                else:
                    self.__import_file(f, module, args)

    def create_mapset(self, mapset, dbase=None, location=None):
        module = 'g.mapset'
        gs.run_command(module, mapset=mapset, dbase=dbase, location=location)

    def print_products(self):
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
    for key, value in dictionary.items():
        if value == old_value:
            dictionary[key] = new_value

    return dictionary


def main():
    options, flags = gs.parser()

    for keys, values in options.items():
        value_temp = values.split(',')

        if len(value_temp) == 1:
            pass
        else:
            options[keys] = tuple(value_temp)

    options = change_dict_value(options, '', None)

    importer = Finder(options['input_dir'], recursive=flags['e'], sensor=options['sensor'],
                      projection=options['projection'], orbit=options['orbit'], polarization=options['polarization'],
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
    sys.exit(main())
