* Maybe change topnumber to 2 and dbtopnumber to 1
* Caves with large number of entrances (such as CCC) cause the entrance block
  to run off the page.
* Ability to tail the build log from the web interface
* Fix latex escaping
* Support markdown on text area input fields. Current latex code embedded in
  Tucker County descriptions: \textbf{}, \textit{}, \subsection*{}
* DVD ZIP file (from finalize-tucker-county-cd):
  - wget -O "$NEWCD/Surface Photos/Drainage Tunnel Near Spruce Lick Run - Masney.jpg" http://farm3.static.flickr.com/2631/4137642653_e95627df1c_b.jpg 
  - wget -O "$NEWCD/Surface Photos/Cross Bedded Limestone Outcrop Along Otter Creek - Masney.jpg" http://farm3.static.flickr.com/2336/3537779054_697ce259bb_b.jpg
  - mv "$NEWCD/Surface Photos/Cave Hollow-Arbogast System Surface Photo - 1 of 2 - Masney.jpg" "$NEWCD/Surface Photos/Dragfold Outside Cave Hollow Entrance - Masney.jpg"
  - mv "$NEWCD/Surface Photos/Cave Hollow-Arbogast System Surface Photo - 2 of 2.jpg" "$NEWCD/Surface Photos/Rufus Maxwell - AT Bonnifield - Abraham Bonnifield.jpg"
* Combine hillshade and topo maps. Make hillshade maps a bit more colorful.
  See http://blog.mastermaps.com/2012/07 for examples.
* Migrate from Python 2.7 to Python 3.
* Upgrade from Django 1.8 to Django 1.10 (or later if available).
* Add units field to length and depth on web interface
* Automatically generate the survey ID field
* Add 11 reasons a cave can be significant to WVASS
* Remove bulletin id off of attachment filenames
* Allow specifying the specific entrance when uploading entrance photos.
* Allow referencing an attachment on another feature
