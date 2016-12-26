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
import cavedb.settings
import cavedb.utils

class Shp(cavedb.docgen_common.Common):
    def __init__(self, basedir, bulletin, gis_x_buffer=0.005, gis_y_buffer=0.005):
        cavedb.docgen_common.Common.__init__(self, basedir, bulletin)
        self.buildscript = ''

        self.shp_zip_file = cavedb.utils.get_shp_filename(self.bulletin.id)
        self.shp_dir = os.path.dirname(self.shp_zip_file)

        self.gis_x_buffer = gis_x_buffer
        self.gis_y_buffer = gis_y_buffer

        self.overall_extents = None
        self.region_extents = {}

        self.gis_maps = {}


    def open(self, all_regions_gis_hash):
        self.overall_extents = init_extents(None, all_regions_gis_hash)
        cavedb.docgen_common.create_directory(self.shp_dir)


    def gis_map(self, gismap):
        gis_options = {}
        gis_options['basename'] = gismap.name
        gis_options['path'] = '%s/%s.map' % (self.shp_dir, gismap.name)
        gis_options['fd'] = open(gis_options['path'], 'w')

        write_mapserver_header(gis_options)

        self.gis_maps[gismap.name] = gis_options


    def gis_layer(self, layer):
        for gismap_basename in layer.maps.all():
            write_layer(self.gis_maps[gismap_basename.name], layer)


    def gis_lineplot(self, lineplot, lineplot_type, shpfilename):
        if lineplot_type == 'underground':
            for gis_options in self.gis_maps.values():
                write_lineplot(gis_options, lineplot, shpfilename)


    def begin_region(self, region, gis_region_hash, map_name):
        if not region.show_gis_map:
            return

        self.region_extents[region.id] = init_extents(region.region_name, gis_region_hash)


    def feature_entrance(self, feature, entrance, coordinates):
        if self.region_extents[feature.bulletin_region.id]:
            self.update_extent_boundary(self.overall_extents, coordinates)
            self.update_extent_boundary(self.region_extents[feature.bulletin_region.id], \
                                        coordinates)


    def close(self):
        locs_ovffile = self.write_locations_ovf()

        extents_csvfile = self.write_region_extents_csv()
        extents_ovffile = self.write_region_extents_ovf(extents_csvfile)

        self.buildscript = 'ogr2ogr -f "ESRI Shapefile" "%s" "%s"\n' % \
                           (self.shp_dir, locs_ovffile) + \
                           'ogr2ogr -f "ESRI Shapefile" "%s" "%s"\n' % \
                           (self.shp_dir, extents_ovffile) + \
                           'cd %s\n' % (self.shp_dir) + \
                           'zip %s *.{shp,shx,dbf,prj}\n' % (self.shp_zip_file)

        for gis_options in self.gis_maps.values():
            write_mapserver_footer(gis_options)
            gis_options['fd'].close()


    def write_region_extents_csv(self):
        csvfile = '%s/region_extents.csv' % (self.shp_dir)
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

        locs_ovffile = '%s/karst_feature_locations.ovf' % (self.shp_dir)
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

        create_epsg_4326_prjfile('%s/karst_feature_locations.prj' % (self.shp_dir))

        return locs_ovffile


    def write_region_extents_ovf(self, csvfile):
        extents_ovffile = '%s/region_extents.ovf' % (self.shp_dir)
        with open(extents_ovffile, 'w') as output:
            output.write('<OGRVRTDataSource>')
            output.write('<OGRVRTLayer name="region_extents">')
            output.write('<SrcDataSource>%s</SrcDataSource>' % (csvfile))
            output.write('<SrcLayer>region_extents</SrcLayer>')
            output.write('<GeometryType>wkbPolygon</GeometryType>')
            output.write('<GeometryField encoding="WKT" field="wkt"/>')
            output.write('</OGRVRTLayer>')
            output.write('</OGRVRTDataSource>')

        create_epsg_4326_prjfile('%s/region_extents.prj' % (self.shp_dir))

        return extents_ovffile


    def generate_buildscript(self):
        return self.buildscript


    def update_extent_boundary(self, extents, coordinates):
        if not extents['minx'] or coordinates.wgs84_lon - self.gis_x_buffer < extents['minx']:
            extents['minx'] = coordinates.wgs84_lon - self.gis_x_buffer

        if not extents['miny'] or coordinates.wgs84_lat - self.gis_y_buffer < extents['miny']:
            extents['miny'] = coordinates.wgs84_lat - self.gis_y_buffer

        if not extents['maxx'] or coordinates.wgs84_lon + self.gis_x_buffer > extents['maxx']:
            extents['maxx'] = coordinates.wgs84_lon + self.gis_x_buffer

        if not extents['maxy'] or coordinates.wgs84_lat + self.gis_y_buffer > extents['maxy']:
            extents['maxy'] = coordinates.wgs84_lat + self.gis_y_buffer



def create_epsg_4326_prjfile(prjfile):
    with open(prjfile, 'w') as output:
        output.write('GEOGCS["WGS 84",' + \
                     'DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,' + \
                     'AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],' + \
                     'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,' + \
                     'AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,' + \
                     'AUTHORITY["EPSG","9122"]],' + \
                     'AUTHORITY["EPSG","4326"]]')


def init_extents(name, gishash):
    ret = {}
    ret['name'] = name
    ret['gishash'] = gishash
    ret['minx'] = None
    ret['miny'] = None
    ret['maxx'] = None
    ret['maxy'] = None
    return ret


def write_mapserver_header(gis_options):
    mapfile = gis_options['fd']

    mapfile.write('MAP\n')
    mapfile.write('  IMAGETYPE JPEG\n')
    mapfile.write('  SIZE 2100 2100\n')
    mapfile.write('  IMAGECOLOR 255 255 255\n')
    mapfile.write('  FONTSET "fonts.list"\n')
    mapfile.write('  OUTPUTFORMAT\n')
    mapfile.write('    NAME "aggjpg24"\n')
    mapfile.write('    DRIVER AGG/JPEG\n')
    mapfile.write('    MIMETYPE "image/jpeg"\n')
    mapfile.write('    IMAGEMODE RGB\n')
    mapfile.write('    EXTENSION "jpg"\n')
    mapfile.write('  END\n')
    mapfile.write('  SYMBOL\n')
    mapfile.write('    NAME "point"\n')
    mapfile.write('    TYPE ELLIPSE\n')
    mapfile.write('    POINTS\n')
    mapfile.write('      1 1\n')
    mapfile.write('    END\n')
    mapfile.write('    FILLED TRUE\n')
    mapfile.write('  END\n')
    mapfile.write('  UNITS dd\n')
    mapfile.write('  PROJECTION\n')
    mapfile.write('    "proj=longlat"\n')
    mapfile.write('    "ellps=WGS84"\n')
    mapfile.write('    "datum=WGS84"\n')
    mapfile.write('    "no_defs"\n')
    mapfile.write('  END\n')
    mapfile.write('  LEGEND\n')
    mapfile.write('    KEYSIZE 36 36\n')
    mapfile.write('    LABEL\n')
    mapfile.write('      SIZE 24\n')
    mapfile.write('      TYPE TRUETYPE\n')
    mapfile.write('      FONT opensymbol\n')
    mapfile.write('      ANTIALIAS TRUE\n')
    mapfile.write('      COLOR 0 0 89\n')
    mapfile.write('      POSITION cc\n')
    mapfile.write('    END\n')
    mapfile.write('    STATUS OFF\n')
    mapfile.write('    POSITION lr\n')
    mapfile.write('    IMAGECOLOR 255 255 255\n')
    mapfile.write('    TRANSPARENT FALSE\n')
    mapfile.write('  END\n')
    mapfile.write('  SCALEBAR\n')
    mapfile.write('    LABEL\n')
    mapfile.write('      SIZE 20\n')
    mapfile.write('      TYPE TRUETYPE\n')
    mapfile.write('      FONT opensymbol\n')
    mapfile.write('      ANTIALIAS TRUE\n')
    mapfile.write('      COLOR 0 0 0\n')
    mapfile.write('    END\n')
    mapfile.write('    STYLE 0\n')
    mapfile.write('    SIZE 600 25\n')
    mapfile.write('    IMAGECOLOR 255 255 255\n')
    mapfile.write('    OUTLINECOLOR 0 0 0\n')
    mapfile.write('    TRANSPARENT FALSE\n')
    mapfile.write('    COLOR 0 0 0\n')
    mapfile.write('    UNITS MILES\n')
    mapfile.write('    INTERVALS 5\n')
    mapfile.write('    STATUS EMBED\n')
    mapfile.write('    POSITION ll\n')
    mapfile.write('  END\n')
    mapfile.write('  INCLUDE "%s/%s.map"\n' % \
                  (cavedb.settings.GIS_INCLUDES_DIR, gis_options['basename']))


def write_layer(gis_options, layer):
    mapfile = gis_options['fd']

    mapfile.write('  LAYER\n')
    mapfile.write('    NAME %s\n' % (layer.table_name))

    if layer.type != 'RASTER':
        mapfile.write('    CONNECTIONTYPE %s\n' % (cavedb.settings.GIS_CONNECTION_TYPE))
        mapfile.write('    CONNECTION %s\n' % (cavedb.settings.GIS_CONNECTION))

    if layer.filename:
        mapfile.write('    DATA %s\n' % (layer.filename))
    else:
        mapfile.write('    DATA geom from %s\n' % (layer.table_name))

    mapfile.write('    STATUS ON\n')
    mapfile.write('    TYPE %s\n' % (layer.type))

    if layer.label_item:
        mapfile.write('    LABELITEM %s\n' % (layer.label_item))

    if layer.type != 'RASTER':
        mapfile.write('    CLASS\n')
        mapfile.write('      STYLE\n')
        mapfile.write('        COLOR %s\n' % (layer.color))

        if not layer.symbol and layer.symbol_size:
            mapfile.write('        WIDTH %s\n' % (layer.symbol_size))

        if layer.line_type == 'Dashed':
            mapfile.write('        LINECAP butt\n')
            mapfile.write('        PATTERN 6 3 3 6 END\n')

        mapfile.write('      END\n')

        # FIXME - duplicate layers
        if layer.description:
            mapfile.write('     NAME "%s"\n' % (layer.description))

        if layer.symbol:
            mapfile.write('     SYMBOL "%s"\n' % (layer.symbol))
            mapfile.write('     SIZE %s\n' % (layer.symbol_size))

        if layer.max_scale:
            mapfile.write('     MAXSCALE %s\n' % (layer.max_scale))

        if layer.label_item:
            mapfile.write('      LABEL\n')
            mapfile.write('        ANGLE AUTO\n')
            mapfile.write('        TYPE TRUETYPE\n')
            mapfile.write('        FONT opensymbol\n')
            mapfile.write('        ANTIALIAS TRUE\n')
            mapfile.write('        POSITION AUTO\n')
            mapfile.write('        PARTIALS TRUE\n')
            mapfile.write('        MINDISTANCE 500\n')
            mapfile.write('        BUFFER 20\n')
            mapfile.write('        MINSIZE 4\n')
            mapfile.write('        COLOR %s\n' % (layer.color))
            mapfile.write('        SIZE %s\n' % (layer.font_size * 2))
            mapfile.write('      END\n')

        mapfile.write('    END\n')

    mapfile.write('  END\n')


def write_lineplot(gis_options, lineplot, shpfilename):
    mapfile = gis_options['fd']

    mapfile.write('  LAYER\n')
    mapfile.write('    NAME lineplot_%s\n' % (lineplot.id))
    mapfile.write('    DATA "%s"\n' % (shpfilename))
    mapfile.write('    STATUS ON\n')
    mapfile.write('    TYPE LINE\n')

    if lineplot.coord_sys == 'UTM' and lineplot.datum == 'NAD27':
        mapfile.write('    PROJECTION\n')
        mapfile.write('      "proj=utm"\n')
        mapfile.write('      "zone=17"\n')
        mapfile.write('      "ellps=clrk66"\n')
        mapfile.write('      "datum=NAD27"\n')
        mapfile.write('      "units=m"\n')
        mapfile.write('      "no_defs"\n')
        mapfile.write('    END\n')
    elif lineplot.coord_sys == 'LATLON' and \
         (lineplot.datum == 'NAD83' or lineplot.datum == 'WGS84'):
        mapfile.write('    PROJECTION\n')
        mapfile.write('      "proj=longlat"\n')
        mapfile.write('      "ellps=WGS84"\n')
        mapfile.write('      "datum=WGS84"\n')
        mapfile.write('      "no_defs"\n')
        mapfile.write('    END\n')

    mapfile.write('    CLASS\n')
    mapfile.write('      SYMBOL "point"\n')
    mapfile.write('      SIZE 2\n')
    mapfile.write('      MAXSCALE 60000.00\n')
    mapfile.write('      COLOR 255 0 0\n')
    mapfile.write('    END\n')
    mapfile.write('  END\n')


def write_mapserver_footer(gis_options):
    mapfile = gis_options['fd']

    mapfile.write('  LAYER\n')
    mapfile.write('    NAME karst_feature_locations\n')
    mapfile.write('    DATA ../shp/karst_feature_locations\n')
    mapfile.write('    STATUS ON\n')
    mapfile.write('    TYPE POINT\n')
    mapfile.write('    PROJECTION\n')
    mapfile.write('      "proj=longlat"\n')
    mapfile.write('      "ellps=WGS84"\n')
    mapfile.write('      "datum=WGS84"\n')
    mapfile.write('      "no_defs"\n')
    mapfile.write('    END\n')
    mapfile.write('    LABELITEM "name"\n')
    mapfile.write('    CLASS\n')
    mapfile.write('      EXPRESSION (\'[significan]\' eq \'yes\')\n')
    mapfile.write('      SYMBOL "point"\n')
    mapfile.write('      SIZE 7\n')
    mapfile.write('      COLOR 0 0 0\n')
    mapfile.write('     MAXSCALE 60000.00\n')
    mapfile.write('      LABEL\n')
    mapfile.write('        ANGLE 45\n')
    mapfile.write('        TYPE TRUETYPE\n')
    mapfile.write('        FONT opensymbol\n')
    mapfile.write('        ANTIALIAS TRUE\n')
    mapfile.write('        POSITION AUTO\n')
    mapfile.write('        PARTIALS TRUE\n')
    mapfile.write('        MINDISTANCE 50\n')
    mapfile.write('        BUFFER 4\n')
    mapfile.write('        MINSIZE 4\n')
    mapfile.write('        COLOR 132 31 31\n')
    mapfile.write('       SIZE 16\n')
    mapfile.write('        PRIORITY [gislbl_pri]\n')
    mapfile.write('      END\n')
    mapfile.write('    END\n')
    mapfile.write('    CLASS\n')
    mapfile.write('      EXPRESSION (\'[type]\' eq \'Cave\')\n')
    mapfile.write('      SYMBOL "point"\n')
    mapfile.write('      SIZE 7\n')
    mapfile.write('      COLOR 0 0 0\n')
    mapfile.write('      MAXSCALE 60000.00\n')
    mapfile.write('      LABEL\n')
    mapfile.write('        ANGLE 45\n')
    mapfile.write('        TYPE TRUETYPE\n')
    mapfile.write('        FONT opensymbol\n')
    mapfile.write('        ANTIALIAS TRUE\n')
    mapfile.write('        POSITION AUTO\n')
    mapfile.write('        PARTIALS TRUE\n')
    mapfile.write('        MINDISTANCE 50\n')
    mapfile.write('        BUFFER 4\n')
    mapfile.write('        MINSIZE 4\n')
    mapfile.write('        COLOR 132 31 31\n')
    mapfile.write('        SIZE 16\n')
    mapfile.write('        PRIORITY [gislbl_pri]\n')
    mapfile.write('      END\n')
    mapfile.write('    END\n')
    mapfile.write('    CLASS\n')
    mapfile.write('      EXPRESSION (\'[type]\' eq \'Cave\')\n')
    mapfile.write('      SYMBOL  "point"\n')
    mapfile.write('      SIZE    7\n')
    mapfile.write('      COLOR 0 0 0\n')
    mapfile.write('      MAXSCALE 60000.00\n')
    mapfile.write('      LABEL\n')
    mapfile.write('        ANGLE 45\n')
    mapfile.write('        TYPE TRUETYPE\n')
    mapfile.write('        FONT opensymbol\n')
    mapfile.write('        ANTIALIAS TRUE\n')
    mapfile.write('        POSITION AUTO\n')
    mapfile.write('        PARTIALS TRUE\n')
    mapfile.write('        MINDISTANCE 50\n')
    mapfile.write('        BUFFER 4\n')
    mapfile.write('        MINSIZE 4\n')
    mapfile.write('        COLOR 132 31 31\n')
    mapfile.write('        SIZE 14\n')
    mapfile.write('        PRIORITY [gislbl_pri]\n')
    mapfile.write('      END\n')
    mapfile.write('    END\n')
    mapfile.write('    CLASS\n')
    mapfile.write('      EXPRESSION (\'[type]\' eq \'FRO\' or \'[type]\' eq \'Sandstone\' or ' + \
                  '\'[type]\' eq \'Spring\' or \'[type]\' eq \'Insurgence\')\n')
    mapfile.write('      SYMBOL  "point"\n')
    mapfile.write('      SIZE    5\n')
    mapfile.write('      COLOR 0 0 0\n')
    mapfile.write('      MAXSCALE 60000.00\n')
    mapfile.write('      LABEL\n')
    mapfile.write('        ANGLE 45\n')
    mapfile.write('        TYPE TRUETYPE\n')
    mapfile.write('        FONT opensymbol\n')
    mapfile.write('        ANTIALIAS TRUE\n')
    mapfile.write('        POSITION AUTO\n')
    mapfile.write('        PARTIALS TRUE\n')
    mapfile.write('        MINDISTANCE 50\n')
    mapfile.write('        BUFFER 4\n')
    mapfile.write('        MINSIZE 4\n')
    mapfile.write('        COLOR 132 31 31\n')
    mapfile.write('        SIZE 12\n')
    mapfile.write('        PRIORITY [gislbl_pri]\n')
    mapfile.write('      END\n')
    mapfile.write('    END\n')
    mapfile.write('  END\n')
    mapfile.write('  LAYER\n')
    mapfile.write('    NAME region_extents\n')
    mapfile.write('    DATA ../shp/region_extents\n')
    mapfile.write('    STATUS  ON\n')
    mapfile.write('    TYPE  POLYGON\n')
    mapfile.write('    PROJECTION\n')
    mapfile.write('      "proj=longlat"\n')
    mapfile.write('      "ellps=WGS84"\n')
    mapfile.write('      "datum=WGS84"\n')
    mapfile.write('      "no_defs"\n')
    mapfile.write('    END\n')
    mapfile.write('    LABELITEM "region_nam"\n')
    mapfile.write('    CLASS\n')
    mapfile.write('      OUTLINECOLOR   255 0 0\n')
    mapfile.write('      MINSCALE 60000\n')
    mapfile.write('      LABEL\n')
    mapfile.write('        COLOR 132 31 31\n')
    mapfile.write('        OUTLINECOLOR 255 255 255\n')
    mapfile.write('        OUTLINEWIDTH 3\n')
    mapfile.write('        TYPE TRUETYPE\n')
    mapfile.write('        FONT opensymbol\n')
    mapfile.write('        SIZE 14\n')
    mapfile.write('        ANTIALIAS TRUE\n')
    mapfile.write('        POSITION cc\n')
    mapfile.write('        PARTIALS TRUE\n')
    mapfile.write('        MINDISTANCE 0\n')
    mapfile.write('        BUFFER 0\n')
    mapfile.write('        FORCE TRUE\n')
    mapfile.write('      END\n')
    mapfile.write('    END\n')
    mapfile.write('  END\n')
    mapfile.write('  LAYER\n')
    mapfile.write('    NAME "grid"\n')
    mapfile.write('    TYPE LINE\n')
    mapfile.write('    STATUS ON\n')
    mapfile.write('    CLASS\n')
    mapfile.write('      COLOR 112 128 144\n')
    mapfile.write('      MINSCALE 60000\n')
    mapfile.write('      LABEL\n')
    mapfile.write('        TYPE TRUETYPE\n')
    mapfile.write('        FONT opensymbol\n')
    mapfile.write('        SIZE 12\n')
    mapfile.write('        POSITION AUTO\n')
    mapfile.write('        PARTIALS FALSE\n')
    mapfile.write('        BUFFER 50\n')
    mapfile.write('        MINDISTANCE 10000000\n')
    mapfile.write('        ANGLE AUTO\n')
    mapfile.write('        POSITION cr\n')
    mapfile.write('        COLOR 255 0 0\n')
    mapfile.write('      END\n')
    mapfile.write('    END\n')
    mapfile.write('    GRID\n')
    mapfile.write('      LABELFORMAT DDMMSS\n')
    mapfile.write('      MININTERVAL 0.125\n')
    mapfile.write('      MAXINTERVAL 0.125\n')
    mapfile.write('    END\n')
    mapfile.write('  END\n')
    mapfile.write('  LAYER\n')
    mapfile.write('    NAME "grid_small"\n')
    mapfile.write('    TYPE LINE\n')
    mapfile.write('    STATUS ON\n')
    mapfile.write('    CLASS\n')
    mapfile.write('      COLOR 112 128 144\n')
    mapfile.write('      MAXSCALE 60000\n')
    mapfile.write('      LABEL\n')
    mapfile.write('        TYPE TRUETYPE\n')
    mapfile.write('        FONT opensymbol\n')
    mapfile.write('        SIZE 12\n')
    mapfile.write('        POSITION AUTO\n')
    mapfile.write('        PARTIALS FALSE\n')
    mapfile.write('        BUFFER 50\n')
    mapfile.write('        MINDISTANCE 10000000\n')
    mapfile.write('        ANGLE AUTO\n')
    mapfile.write('        POSITION cr\n')
    mapfile.write('        COLOR 255 0 0\n')
    mapfile.write('      END\n')
    mapfile.write('    END\n')
    mapfile.write('    GRID\n')
    mapfile.write('      LABELFORMAT DDMMSS\n')
    mapfile.write('      MININTERVAL 0.01666666666666666666\n')
    mapfile.write('      MAXINTERVAL 0.01666666666666666666\n')
    mapfile.write('    END\n')
    mapfile.write('  END\n')
    mapfile.write('END\n')

