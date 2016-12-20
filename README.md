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


## Sample Bulletin

A [sample bulletin](sample-bulletin/sample-bulletin.pdf?raw=1) is available that
shows a PDF that was generated by this application based on the data added
through the web interface. Full instructions about how to recreate this
sample document are below.

Screenshots of the web application and other generated artifacts are available
in the [screenshots](screenshots) directory.


## Some notes about the generated Sample Bulletin PDF

* The title page, preamble page and contributor pages (i, ii, and iii) can
  all be edited in the bulletin section of the web interface. The content
  is styled using LaTeX.
* The Table of Contents on page iv shows the list of bulletin regions
  associated with the bulletin.
* The map on page v shows the position of all of the regions as they relate
  to each other. The rectangles labeled Coopers Rock and Test Region were
  dynamically drawn based on the extent of all features that are present
  inside each region. If you add a new feature outside of the rectangle,
  then the rectangle will be dynamically expanded the next time that
  the bulletin is regenerated.
* The maps on pages 1, 2, 7 and 8 were all dynamically generated based on
  the features associated with each region.
* Additional terms can be added to the index on page 13. Edit the bulletin
  and add your terms to the Indexed Terms section. Separate each term with
  a newline.


## Installation

* These directions have only been tested on a fresh install of Ubuntu 16.04
  running Django 1.8.7.
* Install the [postgis-data-importer](https://github.com/masneyb/postgis-data-importer)
  project to support setting up your GIS layers in a PostgreSQL database.
  * If you are planning to generate the sample bulletin, see the note about
    the GIS data in the How to generate the Sample Bulletin section below before
    you run the `make` command.
* Install package dependencies:
  * `sudo apt-get install -y python-psycopg2 python-django python-imaging python-dateutil python-gdal htmldoc texlive texlive-latex-extra python2.7 libxml2-utils xsltproc zip mapserver-bin ttf-freefont make xgrep`
* Create an empty PostgreSQL database for the cave data:
  `createdb cavedb`
* Update your database settings in _cavedb/settings.py_. Be sure to change
  the SECRET_KEY setting to random data if you are running the server
  on a non-loopback interface.
* Create the tables in the new database: `make installdb`. It will prompt you
  to create a Django admin user that you will use to log into the website.
* Set a user profile for the django user added by the step above:
  `echo "insert into cavedb_caveuserprofile values (1, 1, true, true, true);" | psql cavedb`
* Copy base files required for building the documents
  * `sudo mkdir -p /usr/local/cavedbmanager-data/`
  * `WHOAMI=$(whoami) && sudo chown "${WHOAMI}":"${WHOAMI}" /usr/local/cavedbmanager-data/`
  * `cp -dpRv data/* /usr/local/cavedbmanager-data/`
* Optional: Install sample bulletin data. See the How to generate the Sample
  Bulletin section below for details.
* Start the server: `make run`. The server will only listen to the
  loopback interface. Use `make runRemote` to have it bind to
  all network interfaces. The latter is useful if you are testing
  from inside a virtual machine.


## How to generate the Sample Bulletin

The sample bulletin included with this repository can be generated with
the following procedure.

* Install the West Virginia base data. This is for the GIS layers,
  counties, topo quads, topo quad / county relationships, and UTM zones
  for the entire state.
  `cat sample-bulletin/wv-base-data.sql | psql cavedb`.
* Add the aerial imagery. Be sure to replace the path to your checked out version of the postgis-data-importer project. The 2003.map and 2014.map matches the name column in the cavedb_gisaerialmap table (without the .map extension).
  * `ln -s /home/$(whoami)/postgis-data-importer/download/us_wv/aerial/USDA-2014/2014.map /usr/local/cavedbmanager-data/gis_maps/`. 
  * `ln -s /home/$(whoami)/postgis-data-importer/download/us_wv/aerial/SAMB-2003/JPG/2003.map /usr/local/cavedbmanager-data/gis_maps/`
  * `ln -s /home/$(whoami)/postgis-data-importer/download/us_wv/hillshade/hillshade.map /usr/local/cavedbmanager-data/gis_maps/`
  * `touch /usr/local/cavedbmanager-data/gis_maps/topo.map`
* When importing your GIS data, you only need to include the
  DEMs and aerial imagery for the Aurora, Lake Lynn and Lead Mine
  7.5 minute quads. By default, the import script will download
  the data for these quads, along with all of the other 7.5 minute
  quads in West Virginia that are underlain by karst.
* Copy sample entrance photos and maps:
  `cp -dpRv sample-bulletin/feature_attachments/ /usr/local/cavedbmanager-data/`
* Add sample bulletin data to PostgreSQL:
  `cat sample-bulletin/sample-bulletin.sql | psql cavedb`
* Start the server and log into the web interface.
  * Click on the Bulletins link on the main page. In the documents column,
    click on the generate link. After a few minutes, refresh the page and
    you should see generated documents if everything went well.
  * Build output is stored in
    /usr/local/cavedbmanager-data/bulletins/bulletin_1/bulletin-build-output.txt.
    if you need to troubleshoot any issues.


## Publications

This system was used to publish the book:

* West Virginia Speleological Survey Bulletin #18: The Caves and Karst of
  Tucker County by Doug McCarty and Brian Masney, 2011. Includes 304 cave and
  karst features, 155 photos, and 96 maps; contains CD-ROM with full-sized
  color versions of all maps and photos, plus extras.

This book is available for sale to [NSS members](http://caves.org/) through
the [West Virginia Speleological Survey](http://www.wvass.org/publications.html).
It is also available for purchase through the
[NSS Bookstore](https://bookstore.caves.org/index.php?mode=store&submode=showitem&itemnumber=01-0687)
to NSS members.

