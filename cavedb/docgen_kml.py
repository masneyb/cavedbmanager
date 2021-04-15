# SPDX-License-Identifier: Apache-2.0

from xml.sax.saxutils import escape
import cavedb.docgen_common
import cavedb.utils

class Kml(cavedb.docgen_common.Common):
    def __init__(self, metadata_name, kml_filename, download_url):
        cavedb.docgen_common.Common.__init__(self)
        self.metadata_name = metadata_name
        self.kml_filename = kml_filename
        self.download_url = download_url
        self.kmlfile = None


    def open(self, all_regions_gis_hash):
        cavedb.docgen_common.create_base_directory(self.kml_filename)
        self.kmlfile = open(self.kml_filename, 'w')

        self.kmlfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.kmlfile.write('<kml xmlns="http://earth.google.com/kml/2.2">\n')
        self.kmlfile.write('<Document>\n')
        self.kmlfile.write('<name>%s</name>\n' % escape(self.metadata_name))


    def begin_region(self, region, gis_region_hash):
        self.kmlfile.write('<Folder id="%s">\n' % (region.id))
        self.kmlfile.write('<name>%s</name>\n' % escape(region.region_name))


    def feature_entrance(self, feature, entrance, coordinates):
        self.kmlfile.write('<Placemark id="%s">\n' % feature.id)

        self.kmlfile.write('<name>%s</name>' % \
                           (escape(cavedb.docgen_common.get_entrance_name(feature, entrance))))
        self.kmlfile.write('<description>')
        self.kmlfile.write('<![CDATA[')
        if feature.length_ft:
            self.kmlfile.write('Length: %s\'<br/>\n' % (feature.length_ft))
        if feature.depth_ft:
            self.kmlfile.write('Depth: %s\'<br/>\n' % (feature.depth_ft))
        if feature.description:
            self.kmlfile.write(feature.description)
        self.kmlfile.write(']]>')
        self.kmlfile.write('</description>\n')

        wgs84_lon_lat = coordinates.get_lon_lat_wgs84()

        self.kmlfile.write('<Point>\n')
        self.kmlfile.write('<coordinates>%s,%s,%s</coordinates>' %
                           (wgs84_lon_lat[0], wgs84_lon_lat[1], entrance.elevation_ft))
        self.kmlfile.write('</Point>\n')
        self.kmlfile.write('</Placemark>')


    def end_region(self):
        self.kmlfile.write('    </Folder>\n')


    def close(self):
        self.kmlfile.write('  </Document>\n')
        self.kmlfile.write('</kml>\n')
        self.kmlfile.close()


    def create_html_download_urls(self):
        return self.create_url(self.download_url, 'Google Earth (KML)', self.kml_filename)


def create_for_bulletin(bulletin):
    return Kml(bulletin.bulletin_name, get_bulletin_kml_filename(bulletin.id), \
               'bulletin/%s/kml' % (bulletin.id))


def create_for_global():
    return Kml('All Bulletins', get_global_kml_filename(), None)


def get_bulletin_kml_filename(bulletin_id):
    return '%s/kml/bulletin_%s.kml' % (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)


def get_global_kml_filename():
    return '%s/kml/all.kml' % (cavedb.utils.get_global_output_base_dir())
