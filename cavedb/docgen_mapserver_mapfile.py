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

import cavedb.docgen_common
import cavedb.docgen_gis_common
import cavedb.settings
import cavedb.utils
from cavedb.docgen_gis_common import get_bulletin_mapserver_mapfile

class MapserverMapfile(cavedb.docgen_common.Common):
    def __init__(self, bulletin):
        cavedb.docgen_common.Common.__init__(self)
        self.bulletin = bulletin
        self.gis_maps = {}


    def gis_map(self, gismap):
        shpdir = cavedb.docgen_gis_common.get_bulletin_shp_directory(self.bulletin.id)

        gis_options = {}
        gis_options['basename'] = gismap.name
        gis_options['path'] = get_bulletin_mapserver_mapfile(self.bulletin.id, gismap.name)
        gis_options['locations_shp'] = '%s/%s' % \
                                       (shpdir, cavedb.docgen_gis_common.LOCATIONS_SHP_LAYER_NAME)
        gis_options['extents_shp'] = '%s/%s' % \
                                     (shpdir, \
                                      cavedb.docgen_gis_common.REGION_EXTENTS_SHP_LAYER_NAME)

        cavedb.docgen_common.create_base_directory(gis_options['path'])

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


    def close(self):
        for gis_options in self.gis_maps.values():
            write_mapserver_footer(gis_options)
            gis_options['fd'].close()

        fonts_list = get_mapserver_fonts_list(self.bulletin.id)
        with open(fonts_list, "w") as output:
            output.write(cavedb.settings.GIS_FONTS_LIST)


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
    mapfile.write('      OUTLINECOLOR 255 255 255\n')
    mapfile.write('      OUTLINEWIDTH 3\n')
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
        mapfile.write('    DATA "%s"\n' % (layer.filename))
    else:
        mapfile.write('    DATA "geom from %s"\n' % (layer.table_name))

    mapfile.write('    STATUS ON\n')
    mapfile.write('    TYPE %s\n' % (layer.type))

    if layer.label_item:
        mapfile.write('    LABELITEM "%s"\n' % (layer.label_item))

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
            mapfile.write('        COLOR %s\n' % (layer.font_color))
            mapfile.write('        OUTLINECOLOR 255 255 255\n')
            mapfile.write('        OUTLINEWIDTH 3\n')
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
    mapfile.write('    NAME %s\n' % (cavedb.docgen_gis_common.LOCATIONS_SHP_LAYER_NAME))
    mapfile.write('    DATA %s\n' % (gis_options['locations_shp']))
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
    mapfile.write('        OUTLINECOLOR 255 255 255\n')
    mapfile.write('        OUTLINEWIDTH 3\n')
    mapfile.write('        SIZE 16\n')
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
    mapfile.write('        OUTLINECOLOR 255 255 255\n')
    mapfile.write('        OUTLINEWIDTH 3\n')
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
    mapfile.write('        OUTLINECOLOR 255 255 255\n')
    mapfile.write('        OUTLINEWIDTH 3\n')
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
    mapfile.write('        OUTLINECOLOR 255 255 255\n')
    mapfile.write('        OUTLINEWIDTH 3\n')
    mapfile.write('        SIZE 12\n')
    mapfile.write('        PRIORITY [gislbl_pri]\n')
    mapfile.write('      END\n')
    mapfile.write('    END\n')
    mapfile.write('  END\n')
    mapfile.write('  LAYER\n')
    mapfile.write('    NAME %s\n' % (cavedb.docgen_gis_common.REGION_EXTENTS_SHP_LAYER_NAME))
    mapfile.write('    DATA %s\n' % (gis_options['extents_shp']))
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
    mapfile.write('        OUTLINECOLOR 255 255 255\n')
    mapfile.write('        OUTLINEWIDTH 3\n')
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
    mapfile.write('        OUTLINECOLOR 255 255 255\n')
    mapfile.write('        OUTLINEWIDTH 3\n')
    mapfile.write('      END\n')
    mapfile.write('    END\n')
    mapfile.write('    GRID\n')
    mapfile.write('      LABELFORMAT DDMMSS\n')
    mapfile.write('      MININTERVAL 0.01666666666666666666\n')
    mapfile.write('      MAXINTERVAL 0.01666666666666666666\n')
    mapfile.write('    END\n')
    mapfile.write('  END\n')
    mapfile.write('END\n')


def get_mapserver_fonts_list(bulletin_id):
    return '%s/fonts.list' % (cavedb.docgen_gis_common.get_bulletin_gis_maps_directory(bulletin_id))
