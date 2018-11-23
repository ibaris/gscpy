#! /usr/bin/python2
# -*- coding: utf-8 -*-
############################################################################
#
# MODULE:       i.script
# AUTHOR(S):    Ismail Baris
# PURPOSE:      Create and register a space time dataset
#
# COPYRIGHT:    (C) Ismail Baris and Nils von Norsinski
#
#               This program is free software under the GNU General
#               Public License (>=v2). Read the file COPYING that
#               comes with GRASS for details.
#
#############################################################################

#%module
#% description: Create and register a space time dataset
#% keyword: temporal
#% keyword: map management
#% keyword: create
#% keyword: time
#%end

# Dataset Section ------------------------------------------------------------------------------------------------------
#%option
#% key: output
#% description: Name of the output space time dataset.
#%guisection: Dataset
#%end

#%option
#% key: title
#% type: string
#% description: Title of the new space time dataset
#% required: yes
#% multiple: no
#%guisection: Dataset
#%end

#%option
#% key: description
#% type: string
#% description: Description of the new space time dataset
#% required: yes
#% multiple: no
#%guisection: Dataset
#%end

#%option
#% key: type
#% required: yes
#% description: Datatype.
#% answer: raster
#% options: raster, raster_3d, vector, label, region, group, all
#%guisection: Dataset
#%end

#%option G_OPT_T_TYPE
#% key: temporaltype
#%guisection: Dataset
#%end

#%option
#% key: semantictype
#% type: string
#% description: Semantic type of the space time dataset
#% required: yes
#% multiple: no
#% options: min,max,sum,mean
#% answer: mean
#%guisection: Dataset
#%end

# Filter Section -------------------------------------------------------------------------------------------------------
#%flag
#% key: i
#% description: Ignore case.
#% guisection: Filter
#%end

#%option
#% key: pattern
#% required: no
#% description: The pattern of file names.
#% guisection: Filter
#%end

#%option
#% key: exclude
#% required: no
#% description: Which files or pattern should be excluded?.
#% guisection: Filter
#%end

#%option
#% key: mapset
#% required: no
#% description: Name of mapset to list (default: current search path).
#% guisection: Filter
#%end

#%option
#% key: region
#% required: no
#% description: Name of saved region for map search (default: not restricted).
#% guisection: Filter
#%end

#%option G_OPT_F_SEP
#% key: separator
#% answer: comma
#% label: Field separator character of the input file
#% guisection: Filter
#%end

# Time & Date Section --------------------------------------------------------------------------------------------------
#%option
#% key: start
#% type: string
#% label: Valid start date and time of the first map
#% description: Format for absolute time: "yyyy-mm-dd HH:MM:SS +HHMM", relative time is of type integer.
#% required: no
#% multiple: no
#% guisection: Time & Date
#%end

#%option
#% key: end
#% type: string
#% label: Valid end date and time of all map
#% description: Format for absolute time: "yyyy-mm-dd HH:MM:SS +HHMM", relative time is of type integer.
#% required: no
#% multiple: no
#% guisection: Time & Date
#%end

#%option
#% key: unit
#% type: string
#% label: Time stamp unit
#% description: Unit must be set in case of relative timestamps
#% required: no
#% multiple: no
#% options: years,months,days,hours,minutes,seconds
#% guisection: Time & Date
#%end

#%option
#% key: increment
#% type: string
#% label: Time increment, works only in conjunction with start option
#% description: Time increment between maps for creation of valid time intervals (format for absolute time: NNN seconds, minutes, hours, days, weeks, months, years; format for relative time is of type integer: 5)
#% required: no
#% multiple: no
#% guisection: Time & Date
#%end

#%flag
#% key: t
#% description: Create an interval (start and end time) in case an increment and the start time are provided
#% guisection: Time & Date
#%end

# Optional Section -----------------------------------------------------------------------------------------------------
#%flag
#% key: p
#% description: Print the detected files and exit.
#% guisection: Optional
#%end

#%flag
#% key: l
#% description: List files after registration.
#% guisection: Optional
#%end

#%flag
#% key: m
#% description: Plot files after registration.
#% guisection: Optional
#%end


import os
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


class CRegister(object):
    """
    Create and register a space time dataset.

    Parameters
    ----------
    output : str
        Name of the output space time dataset.
    title : str
        Title of the new space time dataset.
    description : str
        Description of the new space time dataset
    semantictype : {"min", "max", "sum", "mean"}
        Semantic type of the space time dataset. Default is mean.
    type : {'raster', 'raster_3d', 'vector', 'label', 'region', 'group', 'all'}
        Data type(s). Default is raster.
    start : str
        Valid start date and time of the first map. Format for absolute time: "yyyy-mm-dd HH:MM:SS +HHMM", relative
        time is of type integer.
    end : str
        Valid end date and time of all map. Format for absolute time: "yyyy-mm-dd HH:MM:SS +HHMM", relative time is
        of type integer.
    temporaltype : {"absolute", "relative"}
        The temporal type of the space time datase. Default is absolute.
    separator : {"pipe", "comma", "space", "tab", "newline"}
        Field separator character of the input file. Default is comma.
    unit : {"years", "months", "days", "hours", "minutes", "seconds"}
        Time stamp unit. Unit must be set in case of relative timestamps.
    increment : str
        Time increment, works only in conjunction with start option.
        Time increment between maps for creation of valid time intervals (format for absolute time: NNN seconds,
        minutes, hours, days, weeks, months, years; format for relative time is of type integer: 5)
    pattern : str, optional
        The pattern of file names.
    exclude : str, optional
        Which files or pattern should be excluded?
    mapset : str, optional
        Name of mapset to list (default: current search path); '*' for all mapsets in location.
    region : str, optional
        Name of saved region for map search (default: not restricted); '*' for default region

    Attributes
    ----------
    lkwargs : dict
        Attributes for g.list module.
    ckwargs : dict
        Attributes for t.create module.
    rkwargs : dict
        Attributes for t.register module.

    Methods
    -------
    cregister(self, t=False)
        Create and register a space time dataset.
    print_products()
        Print all detected files.
    list()
        List Files for current space time dataset.
    plot()
        Visualize the temporal extents of the dataset.

    Examples
    --------
    The general usage is
    ::
        $ t.c.register [-i-t-p-l-m] output=string title=string description=string start=string [type=string]
        [semantictype=string] [end=string] [temporaltype=string] [separator=string] [pattern=string]
        [exclude=float] [mapset=string] [region=string] [unit=string] [unit=increment] [--verbose] [--quiet]

    Create a mapset that named 'tempmean' and register all raster files that contains `tempmean`
    ::
        $ t.c.register output=tempmean temporaltype=absolute title="Average temperature"
        description="Monthly temperature average in NC [deg C]" pattern="*tempmean" start=2000-01-01
        increment="1 months"

    Create a mapset that named 'tempmean' and register all raster files that contains `tempmean`. Show a plot after
    registration
    ::
        $ t.c.register -m -t output=tempmean temporaltype=absolute title="Average temperature"
        description="Monthly temperature average in NC [deg C]" pattern="*tempmean" start=2000-01-01
        increment="1 months"

    Create a mapset that named 'precip_sum' and register all raster files that contains `precip`. Show a plot after
    registration
    ::
        $ t.c.register -m -t output=precip_sum title="Preciptation"
        description="Monthly precipitation sums in NC [mm]" pattern="*precip" start=2000-01-01
        increment="1 months" semantictype=sum

    Notes
    -----
    **Flags:**
        * i : Ignore case.
        * t : Create an interval (start and end time) in case an increment and the start time are provided
        * p : Print the detected files and exit.
        * l : List files after registration.
        * m : Plot files after registration.
    """

    def __init__(self, output, title, description, start, type='raster', semantictype='mean', end=None,
                 temporaltype='absolute', separator='comma', pattern=None, exclude=None, mapset=None, region=None,
                 unit=None, increment=None):

        # Self Definitions ---------------------------------------------------------------------------------------------
        self.output = output
        self.title = title
        self.description = description
        self.semantictype = semantictype
        self.type = type
        self.start = start
        self.end = end
        self.input = output

        # Initialise Kwargs --------------------------------------------------------------------------------------------
        # < t.create > ------------
        create_input_parameter = [output, temporaltype, title, description]
        __CREATE_KEYS__ = ["output", "temporaltype", "title", "description"]

        self.ckwargs = {}

        for i, item in enumerate(create_input_parameter):
            if item is not None:
                self.ckwargs[__CREATE_KEYS__[i]] = item

        self.ckwargs['type'] = 'strds'

        # < g.list > ------------
        list_input_parameter = [type, separator, pattern, exclude, mapset, region]
        __LIST_KEYS__ = ["type", "separator", "pattern", "exclude", "mapset", "region"]

        self.lkwargs = {}

        for i, item in enumerate(list_input_parameter):
            if item is not None:
                self.lkwargs[__LIST_KEYS__[i]] = item

        # < t.register > ------------
        register_input_parameter = [self.input, type, start, unit, increment]
        __REG_KEYS__ = ["input", "type", "start", "unit", "increment"]

        self.rkwargs = {}

        for i, item in enumerate(register_input_parameter):
            if item is not None:
                self.rkwargs[__REG_KEYS__[i]] = item

        self.rkwargs['maps'] = self.__list_files()

        # Create Pattern and find files --------------------------------------------------------------------------------
        self.files = self.rkwargs['maps']

    # ------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------------------------------------------------------
    def cregister(self, t=False):
        """
        Create and register a space time dataset.

        Parameters
        ----------
        t : bool
            Create an interval (start and end time) in case an increment and the start time are provided.

        Returns
        -------
        None
        """
        self.__t_create()
        self.__t_register(t)

        return 0

    def print_products(self):
        """
        Print all detected files.

        Returns
        -------
        None
        """
        for f in self.files:
            sys.stdout.write(
                'Detected File <{0}> {1}'.format(str(f), os.linesep))

        return 0

    def list(self):
        """
        List Files for current space time dataset.

        Returns
        -------
        None
        """
        try:
            # gs.run_command('t.list', type=self.type)
            gs.run_command('t.rast.list', input=self.input, sep='tab')

        except CalledModuleError as e:
            pass

        return 0

    def plot(self):
        """
        Visualize the temporal extents of the dataset.

        Returns
        -------
        None
        """
        try:
            gs.run_command('g.gui.timeline', inputs=self.input)

        except CalledModuleError as e:
            pass

        return 0

    # ------------------------------------------------------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------------------------------------------------------
    def __list_files(self, i=False, r=False, e=False, t=False, m=False, f=False):
        raw_files = self.__list_files(i, r, e, t, m, f)

        files = list()
        for item in raw_files.keys():
            files.append(item.encode("utf-8"))

        if files is []:
            gs.message(_('No files detected.'))
            return

        return files

    def __maps(self, module, kwargs):
        maps = module + ' '
        for i, (keys, values) in enumerate(kwargs.items()):
            if i < len(kwargs) - 1:
                maps += keys + '=' + values + ' '
            else:
                maps += keys + '=' + values + ' --quiet'

        return '`' + maps + '`'

    def __t_create(self):
        module = 't.create'

        try:
            gs.run_command(module, **self.ckwargs)

        except CalledModuleError as e:
            pass

        return 0

    def __t_register(self, t=False):
        module = 't.register'
        if t:
            flags = 'i'
        else:
            flags = ''

        try:
            gs.run_command(module, flags=flags, **self.rkwargs)

        except CalledModuleError as e:
            pass

        return 0

    def __list_files(self, i=False, r=False, e=False, t=False, m=False, f=False):
        module = "g.list"
        flag = ''
        flag_list = [i, r, e, t, m, f]
        __FLAG__ = ["i", "r", "e", "t", "m", "f"]

        for i, item in enumerate(flag_list):
            if item:
                flag += __FLAG__[i]

        try:
            return gs.parse_command(module, flags=flag, **self.lkwargs)

        except CalledModuleError as e:
            pass

        return 0

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
    cregister = CRegister(output=options['output'], title=options['title'], description=options['description'],
                          semantictype=options['semantictype'], type=options['type'], start=options['start'],
                          end=options['end'], temporaltype=options['temporaltype'],
                          separator=options['separator'], pattern=options['pattern'], exclude=options['exclude'],
                          mapset=options['mapset'], region=options['region'],
                          unit=options['unit'], increment=options['increment'])

    # print cregister.rkwargs

    if flags['p']:
        cregister.print_products()
        return 0

    cregister.cregister(flags['t'])

    if flags['l']:
        cregister.list()

    if flags['m']:
        cregister.plot()

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    options = change_dict_value(options, '', None)
    if options['type'] is None:
        options['type'] = 'raster'

    if options['semantictype'] is None:
        options['semantictype'] = 'mean'

    if options['separator'] is None:
        options['separator'] = 'comma'

    if options['temporaltype'] is None:
        options['temporaltype'] = 'absolute'


    sys.exit(main())
