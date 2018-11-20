import os
import sys
import re
import datetime as dt
from pyroSAR.snap.util import geocode

try:
    import grass.script as gs

except ImportError:
    pass


class Geocode(object):
    def __init__(self, dir, outdir, pattern=None, t_srs=4326, tr=20, polarizations='all', shapefile=None, scaling='dB',
                 geocoding_type='Range-Doppler', removeS1BoderNoise=True, offset=None, externalDEMFile=None,
                 externalDEMNoDataValue=None, externalDEMApplyEGM=True, basename_extensions=None, test=False,
                 verbose=False):

        # Initialize DIRS ----------------------------------------------------------------------------------------------
        self._dir_list = []

        if not os.path.exists(dir):
            gs.fatal(_('Input directory <{}> not exists').format(dir))
        else:
            self.dir = dir

        if not os.path.exists(outdir):
            os.makedirs(outdir)
        else:
            self.outdir = dir

        # Create Pattern and find files --------------------------------------------------------------------------------
        self.extension = '.zip'

        if pattern:
            filter_p = pattern + self.extension
        else:
            filter_p = r'.*.' + self.extension

        self.filter_p = filter_p

        gs.debug('Filter: {}'.format(filter_p), 1)
        self.files = self.__filter(filter_p)

        # Self definitions ---------------------------------------------------------------------------------------------

        self.t_srs = t_srs
        self.tr = tr
        self.polarizations = polarizations
        self.shapefile = shapefile
        self.scaling = scaling
        self.geocoding_type = geocoding_type
        self.removeS1BoderNoise = removeS1BoderNoise
        self.offset = offset
        self.externalDEMFile = externalDEMFile
        self.externalDEMNoDataValue = externalDEMNoDataValue
        self.externalDEMApplyEGM = externalDEMApplyEGM
        self.basename_extensions = basename_extensions
        self.test = test
        self.verbose = verbose

    # ------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------------------------------------------------------
    def geocode(self):
        for infile in self.files:
            if self.verbose:
                sys.stdout.write('Start Time: {0} ----'.format(dt.datetime.utcnow().__str__()))
                sys.stdout.write('Start Processing File: <{0}> {1}'.format(str(os.path.basename(infile)), os.linesep))

            geocode(infile, self.outdir, t_srs=self.t_srs, tr=self.tr, polarizations=self.polarizations,
                    shapefile=self.shapefile, scaling=self.scaling, geocoding_type=self.geocoding_type,
                    removeS1BoderNoise=self.removeS1BoderNoise, offset=self.offset,
                    externalDEMFile=self.externalDEMFile, externalDEMNoDataValue=self.externalDEMNoDataValue,
                    externalDEMApplyEGM=self.externalDEMApplyEGM, test=self.test)

            if self.verbose:
                sys.stdout.write('End Time: {0} ----'.format(dt.datetime.utcnow().__str__()))
                sys.stdout.flush()

    def print_products(self):
        for f in self.files:
            sys.stdout.write('Detected File <{0}> {1}'.format(str(f), os.linesep))

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
