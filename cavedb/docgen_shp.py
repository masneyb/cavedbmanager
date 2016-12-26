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

class Shp(cavedb.docgen_common.Common):
    def __init__(self, basedir, bulletin):
        cavedb.docgen_common.Common.__init__(self, basedir, bulletin)
        self.buildscript = ''
        self.region_extents = {}
        self.gis_x_buffer = 0.005
        self.gis_y_buffer = 0.005


    def begin_region(self, region, gis_region_hash, map_name):
        if not region.show_gis_map:
            return

        self.region_extents[region.id] = {}
        self.region_extents[region.id]['name'] = region.region_name
        self.region_extents[region.id]['minx'] = None
        self.region_extents[region.id]['miny'] = None
        self.region_extents[region.id]['maxx'] = None
        self.region_extents[region.id]['maxy'] = None


    def feature_entrance(self, feature, entrance, coordinates):
        region_id = feature.bulletin_region.id
        if not self.region_extents[region_id]:
            return

        if not self.region_extents[region_id]['minx'] or \
           coordinates.wgs84_lon - self.gis_x_buffer < self.region_extents[region_id]['minx']:
            self.region_extents[region_id]['minx'] = coordinates.wgs84_lon - self.gis_x_buffer

        if not self.region_extents[region_id]['miny'] or \
           coordinates.wgs84_lat - self.gis_y_buffer < self.region_extents[region_id]['miny']:
            self.region_extents[region_id]['miny'] = coordinates.wgs84_lat - self.gis_y_buffer

        if not self.region_extents[region_id]['maxx'] or \
           coordinates.wgs84_lon + self.gis_x_buffer > self.region_extents[region_id]['maxx']:
            self.region_extents[region_id]['maxx'] = coordinates.wgs84_lon + self.gis_x_buffer

        if not self.region_extents[region_id]['maxy'] or \
           coordinates.wgs84_lat + self.gis_y_buffer > self.region_extents[region_id]['maxy']:
            self.region_extents[region_id]['maxy'] = coordinates.wgs84_lat + self.gis_y_buffer


    def close(self):
        shp_zip_file = cavedb.utils.get_shp_filename(self.bulletin.id)
        cavedb.docgen_common.create_base_directory(shp_zip_file)
        shpdir = os.path.dirname(shp_zip_file)

        locs_ovffile = self.write_locations_ovf(shpdir)

        extents_csvfile = self.write_region_extents_csv(shpdir)
        extents_ovffile = self.write_region_extents_ovf(shpdir, extents_csvfile)

        self.buildscript = '# GisLocationsShp\n' + \
                           'ogr2ogr -f "ESRI Shapefile" "%s" "%s"\n' % (shpdir, locs_ovffile) + \
                           'ogr2ogr -f "ESRI Shapefile" "%s" "%s"\n' % (shpdir, extents_ovffile) + \
                           'cd %s\n' % (shpdir) + \
                           'zip %s *.{shp,shx,dbf,prj}\n' % (shp_zip_file)


    def write_region_extents_csv(self, shpdir):
        csvfile = '%s/region_extents.csv' % (shpdir)
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


    def write_region_extents_ovf(self, shpdir, csvfile):
        extents_ovffile = '%s/region_extents.ovf' % (shpdir)
        with open(extents_ovffile, 'w') as output:
            output.write('<OGRVRTDataSource>')
            output.write('<OGRVRTLayer name="region_extents">')
            output.write('<SrcDataSource>%s</SrcDataSource>' % (csvfile))
            output.write('<SrcLayer>region_extents</SrcLayer>')
            output.write('<GeometryType>wkbPolygon</GeometryType>')
            output.write('<GeometryField encoding="WKT" field="wkt"/>')
            output.write('</OGRVRTLayer>')
            output.write('</OGRVRTDataSource>')

        create_prjfile('%s/region_extents.prj' % (shpdir))

        return extents_ovffile


    def write_locations_ovf(self, shpdir):
        csvfile = cavedb.utils.get_csv_filename(self.bulletin.id)
        csv_data_source_name = os.path.basename(csvfile).replace('.csv', '')

        locs_ovffile = '%s/karst_feature_locations.ovf' % (shpdir)
        with open(locs_ovffile, 'w') as output:
            output.write('<OGRVRTDataSource>')
            output.write('<OGRVRTLayer name="karst_feature_locations">')
            output.write('<SrcDataSource>%s</SrcDataSource>' % (csvfile))
            output.write('<SrcLayer>%s</SrcLayer>' % (csv_data_source_name))
            output.write('<GeometryType>wkbPoint</GeometryType>')
            output.write('<GeometryField encoding="PointFromColumns" x="wgs84_lon" y="wgs84_lat" ' +
                         'z="elevation"/>')
            output.write('</OGRVRTLayer>')
            output.write('</OGRVRTDataSource>')

        create_prjfile('%s/karst_feature_locations.prj' % (shpdir))

        return locs_ovffile


    def generate_buildscript(self):
        return self.buildscript


def create_prjfile(prjfile):
    with open(prjfile, 'w') as output:
        output.write('GEOGCS["WGS 84",' + \
                     'DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,' + \
                     'AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],' + \
                     'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,' + \
                     'AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,' + \
                     'AUTHORITY["EPSG","9122"]],' + \
                     'AUTHORITY["EPSG","4326"]]')

