# Copyright 2016-2017 Brian Masney <masneyb@onstation.org>
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
    def __init__(self, metadata_name, gpx_filename, download_url):
        cavedb.docgen_common.Common.__init__(self)
        self.metadata_name = metadata_name
        self.gpx_filename = gpx_filename
        self.download_url = download_url
        self.gpxfile = None


    def open(self, all_regions_gis_hash):
        cavedb.docgen_common.create_base_directory(self.gpx_filename)
        self.gpxfile = open(self.gpx_filename, 'w')

        self.gpxfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.gpxfile.write('<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' + \
                           'xmlns="http://www.topografix.com/GPX/1/1" version="1.1" ' + \
                           'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 ' + \
                           'http://www.topografix.com/GPX/1/1/gpx.xsd">\n')
        self.gpxfile.write('  <metadata>\n')
        self.gpxfile.write('    <name>%s</name>\n' % (escape(self.metadata_name)))
        self.gpxfile.write('  </metadata>\n')


    def feature_entrance(self, feature, entrance, coordinates):
        name = cavedb.docgen_common.get_entrance_name(feature, entrance)

        wgs84_lon_lat = coordinates.get_lon_lat_wgs84()

        self.gpxfile.write('  <wpt lat="%s" lon="%s">\n' % \
                           (wgs84_lon_lat[1], wgs84_lon_lat[0]))
        self.gpxfile.write('    <ele>%s</ele>\n' % (entrance.elevation_ft))
        self.gpxfile.write('    <name>%s</name>\n' % (escape(name)))
        self.gpxfile.write('    <cmt>%s</cmt>\n' % (feature.feature_type))
        self.gpxfile.write('    <desc>%s</desc>\n' % (escape(name)))
        self.gpxfile.write('    <sym>Waypoint</sym>\n')
        self.gpxfile.write('  </wpt>\n')


    def close(self):
        self.gpxfile.write('</gpx>\n')
        self.gpxfile.close()


    def create_html_download_urls(self):
        return self.create_url(self.download_url, 'GPS Unit (GPX)', self.gpx_filename)


def create_for_bulletin(bulletin):
    return Gpx(bulletin.bulletin_name, get_bulletin_gpx_filename(bulletin.id), \
               'bulletin/%s/gpx' % (bulletin.id))


def create_for_global():
    return Gpx('All Bulletins', get_global_gpx_filename(), None)


def get_bulletin_gpx_filename(bulletin_id):
    return '%s/gpx/bulletin_%s.gpx' % (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)


def get_global_gpx_filename():
    return '%s/gpx/all.gpx' % (cavedb.utils.get_global_output_base_dir())
