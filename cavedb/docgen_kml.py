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

class Kml(cavedb.docgen_common.Common):
    def __init__(self, bulletin):
        cavedb.docgen_common.Common.__init__(self, bulletin)
        self.kmlfile = None


    def open(self, all_regions_gis_hash):
        filename = get_kml_filename(self.bulletin.id)
        cavedb.docgen_common.create_base_directory(filename)
        self.kmlfile = open(filename, 'w')

        self.kmlfile.write('<?xml version="1.0" encoding="US-ASCII"?>\n')
        self.kmlfile.write('<kml xmlns="http://earth.google.com/kml/2.2">\n')
        self.kmlfile.write('<Document>\n')
        self.kmlfile.write('<name>%s</name>\n' % (self.bulletin.bulletin_name))


    def begin_region(self, region, gis_region_hash):
        self.kmlfile.write('<Folder id="%s">\n' % (region.id))
        self.kmlfile.write('<name>%s</name>\n' % (region.region_name))


    def feature_entrance(self, feature, entrance, coordinates):
        self.kmlfile.write('<Placemark id="%s" xmlns="http://earth.google.com/kml/2.2">\n' % \
                           (feature.id))

        self.kmlfile.write('<name>%s</name>' % \
                           (escape(cavedb.docgen_common.get_entrance_name(feature, entrance))))
        self.kmlfile.write('<description>')
        if feature.length_ft:
            self.kmlfile.write('Length: %s\'<br/>\n' % (feature.length_ft))
        if feature.depth_ft:
            self.kmlfile.write('Depth: %s\'<br/>\n' % (feature.depth_ft))
        if feature.description:
            self.kmlfile.write(escape(feature.description))
        self.kmlfile.write('</description>\n')

        self.kmlfile.write('<Point>\n')
        self.kmlfile.write('<coordinates>%s,%s,%s</coordinates>' %
                           (coordinates.wgs84_lat, coordinates.wgs84_lon, entrance.elevation_ft))
        self.kmlfile.write('</Point>\n')
        self.kmlfile.write('</Placemark>')


    def end_region(self):
        self.kmlfile.write('    </Folder>\n')


    def close(self):
        self.kmlfile.write('  </Document>\n')
        self.kmlfile.write('</kml>\n')
        self.kmlfile.close()


    def create_html_download_urls(self):
        return self.create_url('/kml', 'Google Earth (KML)', get_kml_filename(self.bulletin.id))


def get_kml_filename(bulletin_id):
    return '%s/kml/bulletin_%s.kml' % (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)
