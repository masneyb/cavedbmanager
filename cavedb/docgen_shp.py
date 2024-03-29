# SPDX-License-Identifier: Apache-2.0

import os
import cavedb.docgen_entrance_csv
import cavedb.docgen_gis_common
import cavedb.utils

class Shp(cavedb.docgen_gis_common.GisCommon):
    def __init__(self, shp_zip_file, shp_dir, csv_filename, download_url, \
                 gis_x_buffer=0.005, gis_y_buffer=0.005):
        # pylint: disable=too-many-arguments

        cavedb.docgen_gis_common.GisCommon.__init__(self, gis_x_buffer, gis_y_buffer)
        self.buildscript = ''

        self.shp_zip_file = shp_zip_file
        self.shp_dir = shp_dir
        self.csv_filename = csv_filename
        self.download_url = download_url


    def open(self, all_regions_gis_hash):
        cavedb.docgen_common.create_directory(self.shp_dir)


    def write_region_extents_csv(self):
        csv_filename = '%s/%s.csv' % \
                  (self.shp_dir, cavedb.docgen_gis_common.REGION_EXTENTS_SHP_LAYER_NAME)
        with open(csv_filename, 'w', encoding='utf-8') as output:
            output.write('region_name,wkt\n')
            for region_id, extents in list(self.region_extents.items()):
                extents = self.region_extents[region_id]

                if not extents['minx']:
                    continue

                output.write('"%s","POLYGON((%s %s, %s %s, %s %s, %s %s, %s %s))"\n' % \
                             (extents['name'], \
                              extents['minx'], extents['miny'], \
                              extents['maxx'], extents['miny'], \
                              extents['maxx'], extents['maxy'], \
                              extents['minx'], extents['maxy'], \
                              extents['minx'], extents['miny']))

        return csv_filename


    def write_locations_ovf(self):
        csv_data_source_name = os.path.basename(self.csv_filename).replace('.csv', '')

        locs_ovffile = '%s/%s.ovf' % \
                       (self.shp_dir, cavedb.docgen_gis_common.LOCATIONS_SHP_LAYER_NAME)
        with open(locs_ovffile, 'w', encoding='utf-8') as output:
            output.write('<OGRVRTDataSource>')
            output.write('<OGRVRTLayer name="%s">' % \
                         (cavedb.docgen_gis_common.LOCATIONS_SHP_LAYER_NAME))
            output.write('<SrcDataSource>%s</SrcDataSource>' % (self.csv_filename))
            output.write('<SrcLayer>%s</SrcLayer>' % (csv_data_source_name))
            output.write('<GeometryType>wkbPoint</GeometryType>')
            output.write('<GeometryField encoding="PointFromColumns" x="wgs84_lon" y="wgs84_lat" ' +
                         'z="elevation"/>')
            output.write('</OGRVRTLayer>')
            output.write('</OGRVRTDataSource>')

        create_epsg_4326_prjfile('%s/%s.prj' % \
                                 (self.shp_dir, cavedb.docgen_gis_common.LOCATIONS_SHP_LAYER_NAME))

        return locs_ovffile


    def write_region_extents_ovf(self, csv_filename):
        extents_ovf_filename = '%s/%s.ovf' % \
                          (self.shp_dir, cavedb.docgen_gis_common.REGION_EXTENTS_SHP_LAYER_NAME)
        with open(extents_ovf_filename, 'w', encoding='utf-8') as output:
            output.write('<OGRVRTDataSource>')
            output.write('<OGRVRTLayer name="%s">' % \
                         (cavedb.docgen_gis_common.REGION_EXTENTS_SHP_LAYER_NAME))
            output.write('<SrcDataSource>%s</SrcDataSource>' % (csv_filename))
            output.write('<SrcLayer>%s</SrcLayer>' % \
                         (cavedb.docgen_gis_common.REGION_EXTENTS_SHP_LAYER_NAME))
            output.write('<GeometryType>wkbPolygon</GeometryType>')
            output.write('<GeometryField encoding="WKT" field="wkt"/>')
            output.write('</OGRVRTLayer>')
            output.write('</OGRVRTDataSource>')

        create_epsg_4326_prjfile('%s/%s.prj' % \
                                 (self.shp_dir, \
                                  cavedb.docgen_gis_common.REGION_EXTENTS_SHP_LAYER_NAME))

        return extents_ovf_filename


    def close(self):
        locs_ovffile = self.write_locations_ovf()

        extents_csv_filename = self.write_region_extents_csv()
        extents_ovf_filename = self.write_region_extents_ovf(extents_csv_filename)

        self.buildscript = 'ogr2ogr -overwrite -f "ESRI Shapefile" "%s" "%s" ' % \
                           (self.shp_dir, locs_ovffile) + \
                           '-lco EMPTY_STRING_AS_NULL=yes\n' + \
                           'ogr2ogr -overwrite -f "ESRI Shapefile" "%s" "%s"\n' % \
                           (self.shp_dir, extents_ovf_filename) + \
                           'cd %s/..\n' % (self.shp_dir) + \
                           'rm -rf "%s"\n' % (self.shp_zip_file) + \
                           'zip -r "%s" "%s"/\n' % \
                           (self.shp_zip_file, os.path.basename(self.shp_dir))


    def generate_buildscript(self):
        return self.buildscript


    def create_html_download_urls(self):
        return self.create_url(self.download_url, 'Shapefile (SHP)', self.shp_zip_file)


def create_epsg_4326_prjfile(prjfile):
    with open(prjfile, 'w', encoding='utf-8') as output:
        output.write('GEOGCS["WGS 84",' + \
                     'DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,' + \
                     'AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],' + \
                     'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,' + \
                     'AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,' + \
                     'AUTHORITY["EPSG","9122"]],' + \
                     'AUTHORITY["EPSG","4326"]]')


def create_for_bulletin(bulletin):
    csv_filename = cavedb.docgen_entrance_csv.get_bulletin_csv_filename(bulletin.id)
    shp_zip_file = get_bulletin_shp_zip_filename(bulletin.id)
    shp_dir = cavedb.docgen_gis_common.get_bulletin_shp_directory(bulletin.id)

    return Shp(shp_zip_file, shp_dir, csv_filename, 'bulletin/%s/shp' % (bulletin.id))


def create_for_global():
    csv_filename = cavedb.docgen_entrance_csv.get_global_csv_filename()
    shp_zip_file = get_global_shp_zip_filename()
    shp_dir = cavedb.docgen_gis_common.get_bulletin_shp_directory(cavedb.utils.GLOBAL_BULLETIN_ID)

    return Shp(shp_zip_file, shp_dir, csv_filename, None)


def get_bulletin_shp_zip_filename(bulletin_id):
    return '%s/shp.zip' % (cavedb.utils.get_output_base_dir(bulletin_id))


def get_global_shp_zip_filename():
    return '%s/shp.zip' % (cavedb.utils.get_global_output_base_dir())
