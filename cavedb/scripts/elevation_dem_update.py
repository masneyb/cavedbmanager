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

django.setup()

if len(sys.argv) != 2:
    print 'usage: elevation_dem_update.py <path to DEM directory>'
    sys.exit(1)

dem_dir = sys.argv[1]

all_entrances = []

# FIXME - use NAD83
for entrance in cavedb.models.FeatureEntrance.objects.all():
    coords = cavedb.coord_transform.transform_coordinate(entrance)
    if not coords.nad27_utmeast or not coords.nad27_utmnorth:
        continue

    all_entrances.append((entrance.id, coords.nad27_utmeast, coords.nad27_utmnorth, \
                          entrance.elevation_ft))

print 'Loaded %d entrances\n' % (len(all_entrances))

for f in os.listdir(dem_dir):
    filepath = '%s/%s' % (dem_dir, f)

    if not os.path.isfile(filepath) or not filepath.endswith('.tif'):
        continue

    dataset = osgeo.gdal.Open(filepath, osgeo.gdal.GA_ReadOnly)
    geotransform = dataset.GetGeoTransform()
    min_x = geotransform[0]
    max_y = geotransform[3]
    res_x = abs(geotransform[1])
    res_y = abs(geotransform[5])

    band = dataset.GetRasterBand(1)

    for (entrance_id, xcoord, ycoord, zcoord) in all_entrances:
        down_row = int(math.ceil((max_y - ycoord) / res_y))
        down_col = int(math.ceil((xcoord - min_x) / res_x))
        if down_row > 0  and down_col > 0 and \
             dataset.RasterYSize > down_row and dataset.RasterXSize > down_col:
            down_raster_scan = band.ReadRaster(down_col - 1, down_row - 1, 1, 1)
            down_raster_area = struct.unpack('H' * 1, down_raster_scan)
            lowpoint = int(down_raster_area[0])
            if lowpoint > 0:
                print 'entrance: %s, new_elevation=%s, old_elevation=%s' % \
                      (entrance_id, lowpoint, zcoord)
                break

    del dataset
