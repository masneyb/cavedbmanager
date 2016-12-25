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
import cavedb.docgen_common
import cavedb.utils

class GisLocationsShp(cavedb.docgen_common.Common):
    def __init__(self, basedir, bulletin):
        cavedb.docgen_common.Common.__init__(self, basedir, bulletin)
        self.buildscript = ''


    def open(self, all_regions_gis_hash):
        shp_zip_file = cavedb.utils.get_shp_filename(self.bulletin.id)
        cavedb.docgen_common.create_base_directory(shp_zip_file)

        dest_layer_name = os.path.basename(shp_zip_file).replace('.zip', '')
        shpdir = os.path.dirname(shp_zip_file)

        csvfile = cavedb.utils.get_csv_filename(self.bulletin.id)
        csv_data_source_name = os.path.basename(csvfile).replace('.csv', '')

        ovffile = '%s/%s.ovf' % (shpdir, dest_layer_name)
        with open(ovffile, 'w') as output:
            output.write('<OGRVRTDataSource>')
            output.write('<OGRVRTLayer name="%s">' % (dest_layer_name))
            output.write('<SrcDataSource>%s</SrcDataSource>' % (csvfile))
            output.write('<SrcLayer>%s</SrcLayer>' % (csv_data_source_name))
            output.write('<GeometryType>wkbPoint</GeometryType>')
            output.write('<GeometryField encoding="PointFromColumns" x="wgs84_lon" y="wgs84_lat" ' +
                         'z="elevation"/>')
            output.write('</OGRVRTLayer>')
            output.write('</OGRVRTDataSource>')

        prjfile = '%s/%s.prj' % (shpdir, dest_layer_name)
        with open(prjfile, 'w') as output:
            output.write('GEOGCS["WGS 84",' + \
                         'DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,' + \
                         'AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],' + \
                         'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,' + \
                         'AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,' + \
                         'AUTHORITY["EPSG","9122"]],' + \
                         'AUTHORITY["EPSG","4326"]]')

        self.buildscript = '# GisLocationsShp\n' + \
                           'ogr2ogr -f "ESRI Shapefile" "%s" "%s"\n' % (shpdir, ovffile) + \
                           'zip %s %s/*.{shp,shx,dbf,prj}' % (shp_zip_file, shpdir)


    def generate_buildscript(self):
        return self.buildscript

