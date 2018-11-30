Import Scripts
--------------
Import Scripts from a package to GRASS GIS.

This class will copy any suitable python file like 'i_dr_import.py' into the GRASS script folder, without
the '.py' extension and changes the name to 'i.dr.import'. This class will exclude such files like
'__init__.py' or 'setup.py'. For more exclusions the parameter `exclusion` can be used.

.. automodule:: gscpy.i_script
   :members: Grassify