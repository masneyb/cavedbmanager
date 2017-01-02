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
import cavedb.utils

class GisMaps(cavedb.docgen_gis_common.GisCommon):
    def __init__(self, bulletin, gis_x_buffer=0.005, gis_y_buffer=0.005):
        cavedb.docgen_gis_common.GisCommon.__init__(self, bulletin, gis_x_buffer, gis_y_buffer)
        self.gismaps = []


    def gis_map(self, gismap):
        self.gismaps.append(gismap.name)


    def generate_buildscript(self):
        buildscr = ''

        for gismap in self.gismaps:
            mapfile = cavedb.docgen_gis_common.get_mapserver_mapfile(self.bulletin.id, \
                                                                     gismap)
            localfile = get_all_regions_gis_map(self.bulletin.id, gismap)

            if self.overall_extents['gishash']:
                buildscr += create_map(mapfile, localfile, self.overall_extents)

            for extents in self.region_extents.values():
                localfile = get_region_gis_map(self.bulletin.id, extents['id'], gismap)
                buildscr += create_map(mapfile, localfile, extents)

            buildscr += '\n'

        return buildscr


def create_map(mapfile, outfile, extents):
    if not extents['minx']:
        return ''

    hashcode_file = outfile + ".hashcode"
    existing_hashcode = get_existing_hashcode(outfile, hashcode_file)
    enabled = '#' if extents['gishash'] == existing_hashcode else ''

    return '%sshp2img -m %s -o %s -e %s %s %s %s\n' % \
           (enabled, mapfile, outfile, \
            extents['minx'], extents['miny'], extents['maxx'], extents['maxy']) + \
           '%sif [ $? = 0 ] ; then\n' % (enabled) + \
           '%s  echo %s > "%s"\n' % (enabled, extents['gishash'], hashcode_file) + \
           '%sfi\n' % (enabled)


def get_existing_hashcode(outfile, hashcode_file):
    if not os.path.exists(outfile):
        return None

    if not os.path.exists(hashcode_file):
        return None

    with open(hashcode_file, 'r') as infile:
        actual_hashcode = infile.read(1024)
        return actual_hashcode.replace('\n', '').replace('\r', '')

    return None


def get_all_regions_gis_map(bulletin_id, map_name):
    return '%s/bulletin_%s_gis_%s_map.jpg' % \
           (cavedb.docgen_gis_common.get_gis_maps_directory(bulletin_id), bulletin_id, map_name)


def get_region_gis_map(bulletin_id, region_id, map_name):
    return '%s/bulletin_%s_region_%s_gis_%s_map.jpg' % \
           (cavedb.docgen_gis_common.get_gis_maps_directory(bulletin_id), bulletin_id, region_id, \
                                                            map_name)
