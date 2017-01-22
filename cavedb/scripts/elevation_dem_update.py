# Copyright 2017 Brian Masney <masneyb@onstation.org>
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Script to update the elevations of the feature entrances based on
# the elevations in the Digital Elevation Models (DEM). It can be ran
# from the command line with:
#
#   cd /path/to/cavedbmanager
#   DJANGO_SETTINGS_MODULE=cavedb.settings \
#     PYTHONPATH=. \
#     python ./cavedb/scripts/elevation_dem_update.py \
#     /usr/local/postgis-data-importer/download/us_wv/dem/

import math
import os
import struct
import sys
import osgeo.gdal
import django
import cavedb.coord_transform
import cavedb.models

def get_all_entrances():
    all_entrances = []

    for entrance in cavedb.models.FeatureEntrance.objects.all():
        coords = cavedb.coord_transform.transform_coordinate(entrance)
        nad83_utm = coords.get_utm_nad83()
        if not nad83_utm[0] or not nad83_utm[1]:
            continue

        all_entrances.append((entrance.id, nad83_utm[0], nad83_utm[1], entrance.elevation_ft))

    return all_entrances


def process_dem(filepath, all_entrances):
    dataset = osgeo.gdal.Open(filepath, osgeo.gdal.GA_ReadOnly)

    top_left_x, res_x, _, top_left_y, _, res_y = dataset.GetGeoTransform()

    bottom_right_x = top_left_x + (dataset.RasterXSize * res_x)
    bottom_right_y = top_left_y + (dataset.RasterYSize * res_y)

    band = dataset.GetRasterBand(1)
    nodata = band.GetNoDataValue()

    for (entrance_id, xcoord, ycoord, orig_zcoord) in all_entrances:
        if not (top_left_x <= xcoord and xcoord <= bottom_right_x and \
                bottom_right_y <= ycoord and ycoord <= top_left_y):
            continue

        down_row = int(math.ceil((top_left_y - ycoord) / abs(res_y)))
        down_col = int(math.ceil((xcoord - top_left_x) / abs(res_x)))

        down_raster_scan = band.ReadRaster(down_col - 1, down_row - 1, 1, 1)
        down_raster_area = struct.unpack('H' * 1, down_raster_scan)
        lowpoint = down_raster_area[0]

        if lowpoint != nodata:
            print 'entrance: %s, new_elevation=%s, old_elevation=%s' % \
                  (entrance_id, int(lowpoint), orig_zcoord)
            # FIXME - pass in callback to update database

    del dataset


def process_all_dems(dem_dir, all_entrances):
    for filename in os.listdir(dem_dir):
        filepath = '%s/%s' % (dem_dir, filename)

        if not os.path.isfile(filepath) or not filepath.endswith('.tif'):
            continue

        process_dem(filepath, all_entrances)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'usage: elevation_dem_update.py <path to DEM directory>'
        sys.exit(1)

    django.setup()
    process_all_dems(sys.argv[1], get_all_entrances())
