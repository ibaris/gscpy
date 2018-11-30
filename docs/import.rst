Import Related Modules
----------------------
These modules are for importing data. Unlike the existing modules, they can import all files in a directory
by considering a certain pattern. Moreover, it is possible to import these data in different ``mapsets``. In addition,
the module ``i_fr_import`` can import ``pyroSAR`` datasets in a directory based on their metadata.

The name of the modules was chosen to ensure conformity with the GRASS GIS conventions. The addition ``r`` stands for
*raster* where the addition ``d`` and ``f`` stand for *directory* and *finder* respectively.

**Note, it is important for the parameter `pattern`  that the asterisk('*') contains a dot (see examples).**

.. automodule:: gscpy.i_import.i_dr_import
   :members: DirImport

.. automodule:: gscpy.i_import.i_fr_import
   :members: FinderImport