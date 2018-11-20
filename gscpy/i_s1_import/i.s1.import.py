#!/usr/bin/env python
#
############################################################################
#
# MODULE:      i.s1.import
# AUTHOR(S):   Ismail Baris
# PURPOSE:     Imports Sentinel 1 data downloaded from Copernicus Open Access Hub
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
#% description: Imports Sentinel 1 satellite data downloaded from Copernicus Open Access Hub.
#% keyword: imagery
#% keyword: satellite
#% keyword: Sentinel
#% keyword: import
#%end

# Input Section --------------------------------------------------------------------------------------------------------
#%option G_OPT_M_DIR
#% key: input
#% description: Name for input directory where downloaded Sentinel data lives
#% required: yes
#%end

# Filter Section -------------------------------------------------------------------------------------------------------
#%option
#% key: pattern
#% description: File name pattern to import
#% guisection: Filter
#%end

#%option
#% key: extension
#% type: string
#% required: no
#% multiple: no
#% answer: ENVI
#% options: ENVI, GEOTIFF
#% description: Which file extension should be imported?:
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

# Print Section --------------------------------------------------------------------------------------------------------
#%flag
#% key: p
#% description: Print raster data to be imported and exit
#% guisection: Print
#%end
"""

import os
import re
import sys

import grass.script as gs

try:
    import grass.script as gs
    from grass.exceptions import CalledModuleError
except ImportError:
    pass

try:
    from osgeo import gdal, osr
except ImportError as e:
    gs.fatal(_("Flag -r requires GDAL library: {}").format(e))


class S1Import(object):
    def __init__(self, dir, pattern=None, extension=None):
        self._dir_list = []

        if not os.path.exists(dir):
            gs.fatal(_('Input directory <{0}> not exists').format(dir))
        else:
            self.dir = dir

        if extension is not None:
            self.extension = extension
        else:
            self.extension = '.img'

        if pattern is not None:
            filter_p = pattern + extension
        else:
            filter_p = r'S1*__*' + extension

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

    def print_products(self):
        for f in self.files:
            # print self.__check_projection(f)
            # print self.__raster_epsg(f)

            sys.stdout.write(
                'Detected File <{0}> {1} (EPSG: {2}){3}'.format(str(f), '1' if self.__check_projection(f) else '0',
                                                                str(self.__raster_epsg(f)), os.linesep))

    # ------------------------------------------------------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------------------------------------------------------
    def __filter(self, filter_p):
        pattern = re.compile(filter_p)
        files = []
        for rec in os.walk(self.dir):
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


def main():
    if options['pattern'] == '':
        pattern = None
    else:
        pattern = options['pattern']

    if options['extension'] == 'ENVI':
        extension = '.img'
    else:
        extension = '.tif*'

    importer = S1Import(options['input'], pattern, extension)

    if flags['p']:
        importer.print_products()

    importer.import_products(flags['r'], flags['l'])

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    sys.exit(main())
