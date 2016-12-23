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
import os.path
import cavedb.docgen_common

class Mxf(cavedb.docgen_common.Common):
    def __init__(self, basedir, bulletin):
        self.basedir = basedir
        self.bulletin = bulletin
        self.number = 1


    def open(self, all_regions_gis_hash):
        self.create_directory('/output/mxf')
        filename = '%s/output/mxf/bulletin_%s.mxf' % (self.basedir, self.bulletin.id)
        self.mxffile = open(filename, 'w')


    def close(self):
        self.mxffile.close()


    def feature_entrance(self, feature, ent, utmzone, nad27_utmeast, nad27_utmnorth, wgs84_lat, \
                         wgs84_lon):
        if (ent.entrance_name):
            name = '%s - %s' % (feature.name, ent.entrance_name)
        else:
            name = feature.name

        self.mxffile.write('%s, %s, \"%s\", \"%s%s\", \"Number: %s Height: %s\", ff0000, 3\n' % \
                           (wgs84_lat, wgs84_lon, name, feature.survey_county.survey_short_name, \
                            feature.survey_id, self.number, ent.elevation_ft))

        self.number = self.number + 1
