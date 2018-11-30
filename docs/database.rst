Database Related Modules
------------------------
In this section, modules are listed which relate to GRASS GIS databases. The modules listed below can create databases
and mapsets.

The modules work with GRASS GIS versions ``['grass70', 'grass71', 'grass72', 'grass73', 'grass74']``.
However, this can easily be extended. To extend the versions, add new GRASS GIS versions to ``self.candidates`` in
``gscpy.g_db.g_c_database``.

The name of the modules was chosen to ensure conformity with the GRASS GIS conventions. The addition c was added to
module ``gscpy.g_db.g_c_mapset`` to signalize that the already existing module ``g.mapset`` is passed with the flag
``-c`` (*create*).

.. automodule:: gscpy.g_db.g_database
   :members: Database

.. automodule:: gscpy.g_db.g_c_mapset
   :members: Mapset