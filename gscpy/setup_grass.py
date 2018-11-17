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

########### SOFTWARE
# query GRASS 7 itself for its GISBASE
startcmd = [grass7bin_win, '--config', 'path']

p = subprocess.Popen(startcmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()

if p.returncode != 0:
    print >>sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
    sys.exit(-1)

gisbase = out.strip('\n\r')

print (gisbase)