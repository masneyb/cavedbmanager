# cavedbmanager

[![Build Status](https://travis-ci.org/masneyb/cavedbmanager.svg?branch=master)](https://travis-ci.org/masneyb/cavedbmanager)

This project simplifies the data management for a state and/or county cave
survey. It eliminates the need for the manual duplication of data, which will
help to save time and minimize errors. The system dynamically generates
the following types of files based on the data that you upload to the database:

* GIS files: SHP, KML (Google Earth), GPX, MXF (Maptech), and images generated
  using Mapserver with your cave locations and cave lineplots overlayed onto
  them.
* A PDF that is suitable for publication.
* ZIP file whose contents include select photos, maps, and references. All of
  the filenames are standardized to a common naming convention. The contents of
  this ZIP file can be written to a CD or DVD and included with the book.
* To-do list
* CSV file (Spreadsheet)

This significantly reduces the hassle of formatting the book and allows the user
to concentrate on the collection of data.

This project is currently used by the 
[West Virginia Speleological Survey](https://www.wvass.org/)
to manage over 5,000 cave and karst features within the state.


## Sample Bulletin

A [sample bulletin](sample-bulletin/sample-bulletin.pdf?raw=1) is available that
shows a PDF that was generated by this application based on the data that as
added through the web interface. Full instructions about how to recreate this
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

The project can be started by running:

    docker-compose up

Open [http://localhost:8000](http://localhost:8000) in your web browser.
The default username / password is admin / password. Once logged in, click on
the Bulletins link on the main page, then click on the generate link in the
documents column. After a few minutes, refresh the page and you should see
the generated documents.

docker-compose sets up three different containers: a database, a web server and
a worker container for building the various documents. The web container
communicates with the worker container via a named pipe.

Note: During initial startup, it will download about 2-3 GB of data, and it will
transform some of the GIS data. On my laptop with an i7 processor, it takes about
15 minutes to complete. About 3 GB of data will be stored in the docker-volumes/
directory outside the container and will be mounted inside the containers
as volumes.


## Publications

This system was used to publish the book:

* West Virginia Speleological Survey Bulletin #18: The Caves and Karst of
  Tucker County by Doug McCarty and Brian Masney, 2011. Includes 304 cave and
  karst features, 155 photos, and 96 maps; contains CD-ROM with full-sized
  color versions of all maps and photos, plus extras.

This book is available for sale to [NSS members](http://caves.org/) through
the [West Virginia Speleological Survey](http://www.wvass.org/).
It is also available for purchase through the
[NSS Bookstore](https://bookstore.caves.org/index.php?mode=store&submode=showitem&itemnumber=01-0687)
to NSS members.


## Contact

Brian Masney <masneyb@onstation.org>
