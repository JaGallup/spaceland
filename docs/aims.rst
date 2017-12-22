Aim of the library
==================

The aim of Spaceland is to provide the fastest and most idiomatic method of reading `ESRI shapefiles`_ in Python 3. To support that aim, the objectives are:


* Read all shape/record from shapefiles as fast as possible
* Be written in idiomatic Python 3 and provide a modern Python 3 interface to shapefiles
* Use built-in types as much as possible (you shouldn't have to know about shapefile/dBase internals to use the data)
* Provide a high-level interface to data in zipped shapefiles
* Provide a low-level interface for those that need it
* Let people convert shapefile data into a more modern formats
* Integrate with orher Python geospatial libraries
* Include as close to 100% test coverage as possible
* Include high-quality documentation on the library and the shapefile format

For further details, see the :doc:`roadmap <roadmap>`.


What it won't do
----------------

Spaceland is read-only. The shapefile should be considered a historical data format since it's not well-suited to our Web-focussed world, and more suitable formats are now available (e.g. GeoJSON, TopoJSON, geospatial databases).

Spaceland won't convert between coordinate systems, nor will it manipulate or analyse the data. But it should integrate with packages that do.


  .. _ESRI shapefiles: http://www.esri.com/library/whitepapers/pdfs/shapefile.pdf
