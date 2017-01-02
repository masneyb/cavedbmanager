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

import cavedb.docgen_common

class GisCommon(cavedb.docgen_common.Common):
    def __init__(self, bulletin, gis_x_buffer=0.005, gis_y_buffer=0.005):
        cavedb.docgen_common.Common.__init__(self, bulletin)
        self.gis_x_buffer = gis_x_buffer
        self.gis_y_buffer = gis_y_buffer

        self.overall_extents = None
        self.region_extents = {}


    def open(self, all_regions_gis_hash):
        self.overall_extents = init_extents(None, None, all_regions_gis_hash)


    def begin_region(self, region, gis_region_hash):
        if not region.show_gis_map or not gis_region_hash:
            return

        self.region_extents[region.id] = init_extents(region.id, region.region_name, \
                                                      gis_region_hash)


    def feature_entrance(self, feature, entrance, coordinates):
        if feature.bulletin_region.id in self.region_extents:
            self.update_extent_boundary(self.overall_extents, coordinates)
            self.update_extent_boundary(self.region_extents[feature.bulletin_region.id], \
                                        coordinates)


    def update_extent_boundary(self, extents, coordinates):
        if not coordinates.wgs84_lat or not coordinates.wgs84_lon:
            return

        if not extents['minx'] or coordinates.wgs84_lon - self.gis_x_buffer < extents['minx']:
            extents['minx'] = coordinates.wgs84_lon - self.gis_x_buffer

        if not extents['miny'] or coordinates.wgs84_lat - self.gis_y_buffer < extents['miny']:
            extents['miny'] = coordinates.wgs84_lat - self.gis_y_buffer

        if not extents['maxx'] or coordinates.wgs84_lon + self.gis_x_buffer > extents['maxx']:
            extents['maxx'] = coordinates.wgs84_lon + self.gis_x_buffer

        if not extents['maxy'] or coordinates.wgs84_lat + self.gis_y_buffer > extents['maxy']:
            extents['maxy'] = coordinates.wgs84_lat + self.gis_y_buffer


def init_extents(region_id, name, gishash):
    ret = {}
    ret['id'] = region_id
    ret['name'] = name
    ret['gishash'] = gishash
    ret['minx'] = None
    ret['miny'] = None
    ret['maxx'] = None
    ret['maxy'] = None
    return ret


LOCATIONS_SHP_LAYER_NAME = 'karst_feature_locations'
REGION_EXTENTS_SHP_LAYER_NAME = 'region_extents'


def get_shp_directory(bulletin_id):
    return '%s/shp' % (cavedb.utils.get_output_base_dir(bulletin_id))


def get_gis_maps_directory(bulletin_id):
    return '%s/gis_maps' % (cavedb.utils.get_output_base_dir(bulletin_id))


def get_mapserver_mapfile(bulletin_id, map_name):
    return '%s/%s.map' % (get_gis_maps_directory(bulletin_id), map_name)
