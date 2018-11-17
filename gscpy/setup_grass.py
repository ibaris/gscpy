"""
Script to load GRASS GIS out of GRASS GIS environment.
"""
import os
import sys
import subprocess

# --------------------------------------------------------------------------------------------------
# Enviromental Settings
# --------------------------------------------------------------------------------------------------
# Define path to GRASS GIS launch skript -------------------------------------------------------
grass7bin_win = r'C:\\Program Files\\QGIS 3.4\\bin\\grass74.bat'

# DATA -----------------------------------------------------------------------------------------
# define GRASS DATABASE
gisdb = r"S:\\Documents\\GRASS_GIS_DB\\GSCPY\\PERMANENT"
# gisdb = os.path.join(os.path.expanduser("~"), "grassdata")

# GRASS GIS SOFTWARE ---------------------------------------------------------------------------
startcmd = [grass7bin_win, '--config', 'path']

p = subprocess.Popen(startcmd, shell=False,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()

if p.returncode != 0:
    print >>sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
    sys.exit(-1)

gisbase = out.strip('\n\r')

# Environmental Variables -----------------------------------------------------------------------
# Set GISBASE environment variable
os.environ['GISBASE'] = gisbase

# the following not needed with trunk
os.environ['PATH'] += os.pathsep + os.path.join(gisbase, 'extrabin')
# add path to GRASS addons
home = os.path.expanduser("~")
os.environ['PATH'] += os.pathsep + \
    os.path.join(home, '.grass7', 'addons', 'scripts')

# define GRASS-Python environment
gpydir = os.path.join(gisbase, "etc", "python")
sys.path.append(gpydir)

# DATA
# Set GISDBASE environment variable
os.environ['GISDBASE'] = gisdb

# import GRASS Python bindings (see also pygrass)
import grass.script.setup as gsetup
import grass.script as gscript