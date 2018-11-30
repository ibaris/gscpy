#!/usr/bin/env python

############################################################################
#
# MODULE:      i.dr.import
# AUTHOR(S):   Ismail Baris
# PURPOSE:     Exports GRASS raster maps from a selection into GDAL supported formats.
#
# COPYRIGHT:   (C) Ismail Baris and Nils von Norsinski
#
#              This program is free software under the GNU General Public
#              License (>=v2). Read the file COPYING that comes with GRASS
#              for details.
#
#############################################################################


#%Module
#% description: Exports GRASS raster maps from a selection into GDAL supported formats.
#% keyword: raster
#% keyword: export
#% keyword: list
#%end

# Input Section --------------------------------------------------------------------------------------------------------
#%flag
#% key: i
#% description: Ignore case.
#% guisection: Input
#%end

#%option
#% key: type
#% required: yes
#% description: Datatype.
#% answer: raster
#% options: raster, raster_3d, vector, label, region, group, all
#%guisection: Input
#%end

#%option
#% key: pattern
#% required: no
#% description: The pattern of file names.
#% guisection: Input
#%end

#%option
#% key: exclude
#% required: no
#% description: Which files or pattern should be excluded?.
#% guisection: Input
#%end

#%option
#% key: mapset
#% required: no
#% description: Name of mapset to list (default: current search path).
#% guisection: Input
#%end

#%option
#% key: region
#% required: no
#% description: Name of saved region for map search (default: not restricted).
#% guisection: Input
#%end

# Output Section -------------------------------------------------------------------------------------------------------
#%option G_OPT_M_DIR
#% key: outdir
#% description: The directory where the files will be downloaded.
#% required: yes
#%guisection: Output
#%end

#%flag
#% key: x
#% description: Consider output name as suffix. Otherwise it is considered as prefix.
#% guisection: Output
#%end

#%option
#% key: output
#% required: no
#% description: Name for output raster file.
#%guisection: Output
#%end

#%option
#% key: createopt
#% required: no
#% description:Creation option(s) to pass to the output format driver.
#%guisection: Output
#%end

#%option
#% key: metaopt
#% required: no
#% description:Metadata key(s) and value(s) to include.
#%guisection: Output
#%end

#%option
#% key: nodata
#% required: no
#% type: integer
#% description: Assign a specified nodata value to output bands.
#%guisection: Output
#%end

# Optional Section -----------------------------------------------------------------------------------------------------
#%flag
#% key: p
#% description: Print the detected files and exit.
#% guisection: Optional
#%end


import os
import sys

try:
    import grass.script as gs
    from grass.exceptions import CalledModuleError
except ImportError:
    raise ImportError("You have to install GRASS GIS to run this program.")

try:
    from osgeo import gdal, osr
except ImportError as e:
    gs.fatal(_("Flag -r requires GDAL library: {}").format(e))

    raise ImportError("You have to install GRASS GIS to run this program.")


class OutLGdal(object):
    """
    Exports GRASS raster maps from a selection into GDAL supported formats.

    Parameters
    ----------
    type : {'raster', 'raster_3d', 'vector', 'label', 'region', 'group', 'all'}
        Data type(s).
    outdir : str
        The directory to write the final files to.
    pattern : str, optional
        The pattern of file names.
    exclude : str, optional
        Which files or patterns should be excluded?
    mapset : str, optional
        Name of mapset to list (default: current search path); '*' for all mapsets in location.
    region : str, optional
        Name of saved region for map search (default: not restricted); '*' for default region
    output : str, optional
        Suffix or prefix to the filename (see parameter suffix.
    createopt : str, optional
        Creation option(s) to pass to the output format driver.
    metaopt : str, optional
        Metadata key(s) and value(s) to include
    nodata : float, optional
        Assign a specified nodata value to output bands
    suffix : bool, optional
        If True, the parameter output is used as suffix. If False (Default) it will be used as prefix.

    Attributes
    ----------
    lkwargs : dict
        Attributes for g.list module.
    ekwargs : dict
        Attributes for out.gdal module.

    Methods
    -------
    list_files(i=False, r=False, e=False, t=False, m=False, f=False)
        List ass detected files. Note, that only flag i works!
     export_files(files)
        Export all detected files.
    print_products()
        Print all detected files.

    Examples
    --------
    The general usage is
    ::
        $ out.l.gdal [-i-x-p] type=string outdir=string [pattern=string] [exclude=string] [mapset=string] [region=string]
        [output=string] [createopt=string] [nodata=float] [--verbose] [--quiet]


    List raster files that ends with 'tempmean' from current mapset to a directory
    ::
        $ out.l.gdal -p type=raster outdir=/home/user/data pattern=*tempmean

    Export raster files that ends with 'tempmean' from current mapset to a directory
    ::
        $ out.l.gdal type=raster outdir=/home/user/data pattern=*tempmean

    Export raster files that ends with 'tempmean' from current mapset to a directory and add the suffix '_export'
    to them::
        $ out.l.gdal -x type=raster outdir=/home/user/data pattern=*tempmean output=_export

    Export all raster files
    ::
        $ out.l.gdal type=raster outdir=/home/user/data

    Notes
    -----
    Note, it is important for the parameter `pattern`  that the asterisk('*') contains a dot (see examples).

    **Flags:**
        * x : Consider output name as suffix. Otherwise it is considered as prefix.
        * i : Ignore case.
        * p : Print the detected files and exit.

    """

    def __init__(self, type, outdir, pattern=None, exclude=None, mapset=None, region=None,
                 output=None, createopt=None, metaopt=None, nodata=None, suffix=False):

        # Initialize Directory -----------------------------------------------------------------------------------------
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        else:
            self.outdir = outdir

        # Create Pattern and find files --------------------------------------------------------------------------------
        self.type = type
        self.exclude = exclude
        self.mapset = mapset
        self.region = region
        self.format = 'GTiff'
        self.output = output
        self.createopt = createopt
        self.metaopt = metaopt
        self.nodata = nodata
        self.suffix = suffix

        list_input_parameter = [pattern, exclude, mapset, region]
        __LIST_KEYS__ = ["pattern", "exclude", "mapset", "region"]

        self.lkwargs = {}

        for i, item in enumerate(list_input_parameter):
            if item is not None:
                self.lkwargs[__LIST_KEYS__[i]] = item

        export_input_parameter = [createopt, metaopt, nodata]
        __EXPORT_KEYS__ = ["createopt", "metaopt", "nodata"]

        self.ekwargs = {}

        for i, item in enumerate(export_input_parameter):
            if item is not None:
                self.ekwargs[__EXPORT_KEYS__[i]] = item

    # ------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------------------------------------------------------
    def list_files(self, i=False, r=False, e=False, t=False, m=False, f=False):
        raw_files = self.__list_files(i, r, e, t, m, f)

        files = list()
        for item in raw_files.keys():
            files.append(item.encode("utf-8"))

        if files is []:
            gs.message(_('No files detected.'))
            return

        return files

    def export_files(self, files):
        for file in files:
            if self.output is None:
                output = os.path.join(self.outdir, file + '.tif')

            else:
                if self.suffix:
                    output = os.path.join(self.outdir, file + self.output + '.tif')
                else:
                    output = os.path.join(self.outdir, self.output + file + '.tif')

            self.__export_list(file, output)

    def print_products(self, files):
        """
        Print all detected files.

        Returns
        -------
        None
        """
        for f in files:
            sys.stdout.write(
                'Detected File <{0}> {1}'.format(str(f), os.linesep))

    # ------------------------------------------------------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------------------------------------------------------
    def __list_files(self, i=False, r=False, e=False, t=False, m=False, f=False):
        module = "g.list"
        flag = ''
        flag_list = [i, r, e, t, m, f]
        __FLAG__ = ["i", "r", "e", "t", "m", "f"]

        for i, item in enumerate(flag_list):
            if item:
                flag += __FLAG__[i]

        try:
            return gs.parse_command(module, flags=flag, type=self.type, **self.lkwargs)

        except CalledModuleError as e:
            pass

    def __export_list(self, filename, output):
        module = 'r.out.gdal'

        try:
            gs.run_command(module, input=filename, output=output, **self.ekwargs)

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
    exporter = OutLGdal(type=options['type'], outdir=options['outdir'],
                        pattern=options['pattern'],
                        exclude=options['exclude'], mapset=options['mapset'], region=options['region'],
                        output=options['output'], createopt=options['createopt'], metaopt=options['metaopt'],
                        nodata=options['nodata'],
                        suffix=flags['x'])

    files = exporter.list_files(i=flags['i'])

    if flags['p']:
        exporter.print_products(files)
        return 0

    exporter.export_files(files)

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    options = change_dict_value(options, '', None)

    sys.exit(main())
