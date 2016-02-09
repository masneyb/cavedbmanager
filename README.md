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
* To-do list
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

* These directions have only been tested on a fresh install of Ubuntu
  Server 12.04. Support for a newer release is coming soon.
* Install the [postgis-data-importer](https://github.com/masneyb/postgis-data-importer)
  project to support setting up your GIS layers in a PostgreSQL database. The
  installation for that project does not support the older releases of PostGIS
  found in Ubuntu 12.04. It can be setup with these steps:
  * `sudo apt-get install git make unzip postgis postgresql-client postgresql-9.1 postgresql-9.1-postgis gdal-bin`
  * `MY_USER=$(whoami) && sudo -u postgres createuser -s "${MY_USER}"`
  * `createdb wvgis`
  * `cat /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql | psql wvgis`
  * `cat /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql | psql wvgis`
  * `git clone https://github.com/masneyb/postgis-data-importer.git`
  * `cd postgis-data-importer/`
  * If you are planning to generate the sample bulletin, see the note about
    the GIS data in the Sample Bulletin section below.
  * `make us_wv`
* Install package dependencies: `sudo apt-get install -y mysql-client mysql-server python-mysqldb python-django python-imaging python-dateutil python-gdal htmldoc texlive texlive-latex-extra python2.7 apache2 libapache2-mod-python python-boto postgresql-9.1 postgresql-9.1-postgis postgresql-client-9.1 postgresql-client-common postgresql-common postgis gdal-bin libgeotiff2 libxml2-utils xsltproc zip xgrep mapserver-bin ttf-freefont make`
* Create an empty MySQL database for the cave data:
  `echo "create database cavedb;" | mysql -uroot`
* Update your database settings in _settings.py_. Be sure to change
  the SECRET_KEY setting to random data if you are running the server
  on a non-loopback interface.
* Create the tables in the new database: `make installdb`. It will prompt you
  to create a Django admin user that you will use to log into the website.
* Set a user profile for the django user added by the step above:
  `echo "insert into cavedb_caveuserprofile values (1, 1, 1, 1, 1);" | mysql -uroot cavedb`
* Copy base files required for building the documents
  * `sudo mkdir -p /usr/local/cavedbmanager-data/`
  * `sudo cp -dpRv data/* /usr/local/cavedbmanager-data/`
  * `WHOAMI=$(whoami) && sudo chown -R "${WHOAMI}":"${WHOAMI}" /usr/local/cavedbmanager-data/`
* Optional: Install sample bulletin data. See Sample Bulletin section below
  for details.
* Start the server: `make run`. The server will only listen to the
  loopback interface. Use `make runRemote` to have it bind to
  all network interfaces. The latter is useful if you are testing
  from inside a virtual machine.

## Sample Bulletin

The sample bulletin included with this repository can be generated with
the following procedure.

* Install the West Virginia base data. This is for the GIS layers,
  counties, topo quads, topo quad / county relationships, and UTM zones
  for the entire state.
  * `cat sample-bulletin/wv-base-data.sql | mysql -uroot cavedb`.
  * `sudo ln -s /home/ubuntu/postgis-data-importer/download/us_wv/aerial/USDA-2014/2014.map /usr/local/cavedbmanager-data/gis_maps/`. Be sure to replace the path to your checked out version of the postgis-data-importer project. The 2014 matches the name column in the cavedb_gisaerialmap table.
* When importing your GIS data, you will only need to include the
  DEMs and aerial imagery for these 7.5 minute quads: Aurora,
  Lake Lynn and Lead Mine.
* Copy sample bulletin feature attachments:
  `cp -dpRv sample-bulletin/feature_attachments/ /usr/local/cavedbmanager-data/`
* Add sample bulletin data to MySQL:
  `cat sample-bulletin/sample-bulletin.sql | mysql -uroot cavedb`
* Start the server and log into the web interface. Click on the
  Bulletins link on the main page. In the documents column, click on
  the generate link. After a few minutes, refresh the page and you
  should see generated documents if everything went well. Build output
  is stored in
  /usr/local/cavedbmanager-data/bulletins/bulletin_1/bulletin-build-output.txt.
  if you need to troubleshoot any issues.

