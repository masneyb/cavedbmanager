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

import cavedb.docgen_common

class Gpx(cavedb.docgen_common.Common):
    def __init__(self, basedir, bulletin):
        cavedb.docgen_common.Common.__init__(self, basedir, bulletin)


    def open(self, all_regions_gis_hash):
        self.create_directory('/output/gpx')
        filename = '%s/output/gpx/bulletin_%s.gpx' % (self.basedir, self.bulletin.id)
        self.gpxfile = open(filename, 'w')

        self.gpxfile.write('<?xml version="1.0" encoding="US-ASCII"?>\n')
        self.gpxfile.write('<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' + \
                           'xmlns="http://www.topografix.com/GPX/1/1" version="1.1" ' + \
                           'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 ' + \
                           'http://www.topografix.com/GPX/1/1/gpx.xsd">\n')
        self.gpxfile.write('  <metadata>\n')
        self.gpxfile.write('    <name>%s</name>\n' % (self.bulletin.bulletin_name))
        self.gpxfile.write('  </metadata>\n')


    def feature_entrance(self, feature, ent, utmzone, nad27_utmeast, nad27_utmnorth, wgs84_lat, \
                         wgs84_lon):
        if ent.entrance_name:
            name = '%s - %s' % (feature.name, ent.entrance_name)
        else:
            name = feature.name

        self.gpxfile.write('  <wpt lat="%s" lon="%s">\n' % (wgs84_lat, wgs84_lon))
        self.gpxfile.write('    <ele>%s</ele>\n' % (ent.elevation_ft))
        self.gpxfile.write('    <name>%s</name>\n' % (name))
        self.gpxfile.write('    <cmt>%s</cmt>\n' % (feature.feature_type))
        self.gpxfile.write('    <desc>%s</desc>\n' % (name))
        self.gpxfile.write('    <sym>Waypoint</sym>\n')
        self.gpxfile.write('  </wpt>\n')


    def close(self):
        self.gpxfile.write('</gpx>\n')
        self.gpxfile.close()

