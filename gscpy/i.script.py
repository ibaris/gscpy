#!/usr/bin/env python

############################################################################
#
# MODULE:       i.script
# AUTHOR(S):    Ismail Baris
# PURPOSE:      Import Scripts from a package to GRASS GIS. Maybe requires sudo.
#
# COPYRIGHT:    (C) Ismail Baris and Nils von Norsinski
#
#               This program is free software under the GNU General
#               Public License (>=v2). Read the file COPYING that
#               comes with GRASS for details.
#
#############################################################################

"""
#%Module
#% description: Import Scripts from a package to GRASS GIS.
#% keyword: script
#% keyword: auxiliary
#% keyword: import
#%end

# Input Section --------------------------------------------------------------------------------------------------------
#%option G_OPT_M_DIR
#% key: input
#% description: Directory of python files:
#% required: yes
#%guisection: Input
#%end

#%option G_OPT_M_DIR
#% key: export
#% description: Script directory of GRASS GIS (for Linux it can be detect automatically):
#% required: no
#%guisection: Input
#%end

# Filter Section -------------------------------------------------------------------------------------------------------
#%option
#% key: pattern
#% description: File name pattern to import:
#% guisection: Filter
#%end

#%option
#% key: exclusion
#% description: Which files or pattern should be excluded?:
#% guisection: Filter
#%end

# Optional Section -----------------------------------------------------------------------------------------------------
#%flag
#% key: p
#% description: Print python data to be imported and exit
#% guisection: Optional
#%end

#%flag
#% key: r
#% description: Replace script
#% guisection: Optional
#%end
"""
import os
import re
import shutil
import sys

try:
    import grass.script as gs
except ImportError:
    pass


class Grassify(object):
    def __init__(self, dir, export_path=None, pattern=None, exclusion=None):

        # Self Definitions ---------------------------------------------------------------------------------------------
        self.extension = '.py'

        self.candidates = ['grass70', 'grass71', 'grass72', 'grass73', 'grass74']
        if exclusion is None:
            self.exclusion = ['__init__.py', '__version__.py', 'setup_grass.py', 'gscpy.py', 'setup.py']
        else:
            self.exclusion = exclusion

        # Initialize Directory -----------------------------------------------------------------------------------------
        if not os.path.exists(dir):
            gs.fatal(_('Input directory <{0}> not exists').format(dir))
        else:
            self.import_path = dir

        # < Try to find the script directory of GRASS GIS > ------------
        if export_path is None:
            for item in self.candidates:
                export_path = '/usr/lib/' + item + '/scripts'

                if os.path.exists(export_path):
                    self.export_path = export_path

        elif export_path is not None:
            if not os.path.exists(export_path):
                os.makedirs(export_path)

            self.export_path = export_path

        # Create Pattern and find files --------------------------------------------------------------------------------
        if pattern is None:
            filter_p = '.*' + self.extension
        else:
            filter_p = pattern

        gs.debug('Filter: {}'.format(filter_p), 1)
        self.files = self.__filter(filter_p)

        if self.files is []:
            gs.message(_('No files detected. Note, that must be a point for * like: pattern = str.* '))
            return

    # ------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------------------------------------------------------
    def copy(self, replace=False):
        filename = [os.path.basename(item) for item in self.files]
        filename_split = [os.path.splitext(item) for item in filename]

        for i in range(len(filename_split)):
            old_name = self.files[i]
            base = filename_split[i][0]

            new_name = os.path.join(self.export_path, base)

            if not os.path.exists(new_name) or replace:
                shutil.copy(old_name, new_name)
            elif not replace and os.path.exists(new_name):
                gs.fatal(_('Script <{0}> exists. Try to set the replace flag').format(base))

        return 0

    def print_products(self):
        for f in self.files:
            sys.stdout.write('Detected Files <{0}>'.format(f))

    # ------------------------------------------------------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------------------------------------------------------
    def __filter(self, filter_p):
        pattern = re.compile(filter_p)
        files = []

        for rec in os.walk(self.import_path):
            if not rec[-1]:
                continue

            match = filter(pattern.match, rec[-1])
            if match is None:
                continue

            for f in match:
                if f in self.exclusion:
                    pass
                elif f.endswith(self.extension):
                    files.append(os.path.join(rec[0], f))
                else:
                    pass

        return files


def main():
    if options['pattern'] == '':
        pattern = None
    else:
        pattern = options['pattern']

    if options['exclusion'] == '':
        exclusion = None
    else:
        exclusion = options['exclusion']

    if options['export'] == '':
        export = None
    else:
        export = options['export']

    grassify = Grassify(options['input'], export_path=export, pattern=pattern, exclusion=exclusion)

    if flags['p']:
        grassify.print_products()

    grassify.copy(replace=flags['r'])

    return 0


if __name__ == "__main__":
    options, flags = gs.parser()
    sys.exit(main())
