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

import os
import cavedb.docgen_gis_common
import cavedb.settings
import cavedb.utils

class Shp(cavedb.docgen_gis_common.GisCommon):
    def __init__(self, basedir, bulletin, gis_x_buffer=0.005, gis_y_buffer=0.005):
        cavedb.docgen_gis_common.GisCommon.__init__(self, basedir, bulletin, gis_x_buffer, \
                                                    gis_y_buffer)
        self.buildscript = ''

        self.shp_zip_file = cavedb.utils.get_shp_zip_filename(self.bulletin.id)
        self.shp_dir = cavedb.utils.get_shp_directory(self.bulletin.id)
        cavedb.docgen_common.create_directory(self.shp_dir)


    def close(self):
        locs_ovffile = self.write_locations_ovf()

        extents_csvfile = self.write_region_extents_csv()
        extents_ovffile = self.write_region_extents_ovf(extents_csvfile)

        self.buildscript = 'ogr2ogr -overwrite -f "ESRI Shapefile" "%s" "%s"\n' % \
                           (self.shp_dir, locs_ovffile) + \
                           'ogr2ogr -overwrite -f "ESRI Shapefile" "%s" "%s"\n' % \
                           (self.shp_dir, extents_ovffile) + \
                           'cd %s/..\n' % (self.shp_dir) + \
                           'zip %s %s/*.{shp,shx,dbf,prj}\n' % \
                           (self.shp_zip_file, os.path.basename(self.shp_dir))


    def write_region_extents_csv(self):
        csvfile = '%s/%s.csv' % (self.shp_dir, cavedb.utils.REGION_EXTENTS_SHP_LAYER_NAME)
        with open(csvfile, 'w') as output:
            output.write('region_name,wkt\n')
            for region_id, extents in self.region_extents.items():
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

        return csvfile


    def write_locations_ovf(self):
        csvfile = cavedb.utils.get_csv_filename(self.bulletin.id)
        csv_data_source_name = os.path.basename(csvfile).replace('.csv', '')

        locs_ovffile = '%s/%s.ovf' % (self.shp_dir, cavedb.utils.LOCATIONS_SHP_LAYER_NAME)
        with open(locs_ovffile, 'w') as output:
            output.write('<OGRVRTDataSource>')
            output.write('<OGRVRTLayer name="%s">' % (cavedb.utils.LOCATIONS_SHP_LAYER_NAME))
            output.write('<SrcDataSource>%s</SrcDataSource>' % (csvfile))
            output.write('<SrcLayer>%s</SrcLayer>' % (csv_data_source_name))
            output.write('<GeometryType>wkbPoint</GeometryType>')
            output.write('<GeometryField encoding="PointFromColumns" x="wgs84_lon" y="wgs84_lat" ' +
                         'z="elevation"/>')
            output.write('</OGRVRTLayer>')
            output.write('</OGRVRTDataSource>')

        create_epsg_4326_prjfile('%s/%s.prj' % \
                                 (self.shp_dir, cavedb.utils.LOCATIONS_SHP_LAYER_NAME))

        return locs_ovffile


    def write_region_extents_ovf(self, csvfile):
        extents_ovffile = '%s/%s.ovf' % (self.shp_dir, cavedb.utils.REGION_EXTENTS_SHP_LAYER_NAME)
        with open(extents_ovffile, 'w') as output:
            output.write('<OGRVRTDataSource>')
            output.write('<OGRVRTLayer name="%s">' % (cavedb.utils.REGION_EXTENTS_SHP_LAYER_NAME))
            output.write('<SrcDataSource>%s</SrcDataSource>' % (csvfile))
            output.write('<SrcLayer>%s</SrcLayer>' % (cavedb.utils.REGION_EXTENTS_SHP_LAYER_NAME))
            output.write('<GeometryType>wkbPolygon</GeometryType>')
            output.write('<GeometryField encoding="WKT" field="wkt"/>')
            output.write('</OGRVRTLayer>')
            output.write('</OGRVRTDataSource>')

        create_epsg_4326_prjfile('%s/%s.prj' % \
                                 (self.shp_dir, cavedb.utils.REGION_EXTENTS_SHP_LAYER_NAME))

        return extents_ovffile


    def generate_buildscript(self):
        return self.buildscript


def create_epsg_4326_prjfile(prjfile):
    with open(prjfile, 'w') as output:
        output.write('GEOGCS["WGS 84",' + \
                     'DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,' + \
                     'AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],' + \
                     'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,' + \
                     'AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,' + \
                     'AUTHORITY["EPSG","9122"]],' + \
                     'AUTHORITY["EPSG","4326"]]')

