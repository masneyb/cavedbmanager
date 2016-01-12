# cavedbmanager

A web interface written in Python that is used by the West Virginia
Speleological Survey to manage the list of caves within the state
of West Virginia. The web interface is only available to its members.


## Dependencies

* Python
* Python Imaging Library (python-imaging Debian package)
* Python GDAL Library (python-gdal Debian package)
* Django web framework >= 1.0 (http://www.djangoproject.com/)
* A database such as MySQL (mysql-server-5.0 and mysql-client-5.0 Debian packages)
* Mapserver >= 4.10 (mapserver-bin Debian package)
* LaTeX (texlive Debian package)
* zip Debian package
* xsltproc and libxml2-utils Debian packages
* A webserver such as Apache to serve the content (apache2 Debian package)

I installed the application in /usr/local/cavedbmanager and the application
data in /usr/local/cavedbmanager-data. If you install them in different 
locations, then be sure to edit the main settings.py file with that 
information.

You will also need to setup your GIS maps. Put your GIS layers in 
/usr/local/cavedbmanager-data/gis_maps/layers and edit
/usr/local/cavedbmanager-data/gis_maps/cave.map to customize how those
layers will look on the map. See the Mapserver documentation for more 
information about how to customize it.

