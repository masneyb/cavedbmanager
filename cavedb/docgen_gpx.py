# Copyright 2016 Brian Masney <masneyb@onstation.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from xml.sax.saxutils import escape
import cavedb.docgen_common
import cavedb.utils

class Gpx(cavedb.docgen_common.Common):
    def __init__(self, basedir, bulletin):
        cavedb.docgen_common.Common.__init__(self, basedir, bulletin)


    def open(self, all_regions_gis_hash):
        filename = cavedb.utils.get_gpx_filename(self.bulletin.id)
        cavedb.docgen_common.create_base_directory(filename)
        self.gpxfile = open(filename, 'w')

        self.gpxfile.write('<?xml version="1.0" encoding="US-ASCII"?>\n')
        self.gpxfile.write('<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' + \
                           'xmlns="http://www.topografix.com/GPX/1/1" version="1.1" ' + \
                           'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 ' + \
                           'http://www.topografix.com/GPX/1/1/gpx.xsd">\n')
        self.gpxfile.write('  <metadata>\n')
        self.gpxfile.write('    <name>%s</name>\n' % (escape(self.bulletin.bulletin_name)))
        self.gpxfile.write('  </metadata>\n')


    def feature_entrance(self, feature, entrance, coordinates):
        name = cavedb.docgen_common.get_entrance_name(feature, entrance)

        self.gpxfile.write('  <wpt lat="%s" lon="%s">\n' % \
                           (coordinates.wgs84_lat, coordinates.wgs84_lon))
        self.gpxfile.write('    <ele>%s</ele>\n' % (entrance.elevation_ft))
        self.gpxfile.write('    <name>%s</name>\n' % (escape(name)))
        self.gpxfile.write('    <cmt>%s</cmt>\n' % (feature.feature_type))
        self.gpxfile.write('    <desc>%s</desc>\n' % (escape(name)))
        self.gpxfile.write('    <sym>Waypoint</sym>\n')
        self.gpxfile.write('  </wpt>\n')


    def close(self):
        self.gpxfile.write('</gpx>\n')
        self.gpxfile.close()

