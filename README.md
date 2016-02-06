# cavedbmanager

This project was written to simplify the data management for a state
and/or county cave survey. It eliminates the need for the manual
duplication data, which will help to save time and minimize errors.
This significantly reduces the hassle of formatting the book and
allows the user to concentrate on the collection of data. The
system will dynamically generate various types of files based on
the data that you upload to the database:

* GIS files: SHP, KML (Google Earth), GPX, Maptech, and PNG
  (topo maps and aerial imagery).
* A PDF that is suitable for publication.
* An IS09660 CD/DVD image that can be included with the book that
  includes select entrance photos, maps, and references. All of the
  filenames are standardized to a common naming convetion.
* TODO list
* CSV file (Spreadsheet)

This project is currently used by the West Virginia Speleological Survey
to manage the cave data within the state. The web interface is only
available to its members.

This system was used to publish the book _WVASS Bulletin #18: The
Caves and Karst of Tucker County, WV_. This book is available for
sale to [NSS members](http://caves.org/) through the
[West Virginia Speleological Survey](http://www.wvass.org/publications.html).
It is also available for purchase through the
[NSS Bookstore](https://bookstore.caves.org/index.php?mode=store&submode=showitem&itemnumber=01-0687)
to NSS members.


## Screenshots

Screenshots are available in the [screenshots](screenshots) directory.


## Installation

* These directions have only been tested on Ubuntu 12.04. Support for a newer
  release is coming soon.
* Install the [postgis-data-importer](https://github.com/masneyb/postgis-data-importer)
  project to support setting up your GIS layers in a PostgreSQL database. The
  installation for that project does not support the older releases of PostGIS
  found in Ubuntu 12.04. Create your PostgreSQL database and then install the
  PostGIS extension by running:
  * `cat /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql | psql wvgis`
  * `cat /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql | psql wvgis`
* Install package dependencies: `apt-get install -y mysql-client mysql-server python-mysqldb python-django python-imaging python-dateutil python-gdal htmldoc texlive texlive-latex-extra python2.7 apache2 libapache2-mod-python python-boto postgresql-9.1 postgresql-9.1-postgis postgresql-client-9.1 postgresql-client-common postgresql-common postgis gdal-bin libgeotiff2 libxml2-utils xsltproc zip xgrep mapserver-bin ttf-freefont make`
* Create an empty MySQL database for the cave data:
  `echo "create database cavedb;" | mysql -uroot -proot`
* Update your database settings in _settings.py_. Be sure to change
  the SECRET_KEY setting to random data if you are running the server
  on a non-loopback interface.
* Create the tables in the new database: `make installdb`. It will prompt you
  to create a Django admin user that you will use to log into the website.
* Set a user profile for the django user added by the step above:
  `echo "insert into cavedb_caveuserprofile values (1, 1, 1, 1, 1);" | mysql -uroot -proot cavedb`
* Optional: Install West Virginia base data:
  `cat data/wv-base-data.sql | mysql -uroot -proot cavedb`. This is for the
  GIS layers, counties, topo quads, topo quad / county relationships, and UTM
  zones for the entire state.
* Copy base files required for building the documents
  * `mkdir -p /usr/local/cavedbmanager-data/`
  * `sudo cp -dpRv data/* /usr/local/cavedbmanager-data/`
  * `WHOAMI=$(whoami) && sudo chown -R "${WHOAMI}":"${WHOAMI}" /usr/local/cavedbmanager-data/
* Start the server: `make run`


## Authors

* Brian Masney - [masneyb](https://github.com/masneyb)
* David A. Riggs - [riggsd](https://github.com/riggsd)

