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
import cavedb.utils

class Mxf(cavedb.docgen_common.Common):
    def __init__(self, bulletin):
        cavedb.docgen_common.Common.__init__(self, bulletin)
        self.number = 1
        self.mxffile = None


    def open(self, all_regions_gis_hash):
        filename = get_mxf_filename(self.bulletin.id)
        cavedb.docgen_common.create_base_directory(filename)
        self.mxffile = open(filename, 'w')


    def close(self):
        self.mxffile.close()


    def feature_entrance(self, feature, entrance, coordinates):
        self.mxffile.write('%s, %s, \"%s\", \"%s%s\", \"Number: %s Height: %s\", ff0000, 3\n' % \
                           (coordinates.wgs84_lat, coordinates.wgs84_lon, \
                            cavedb.docgen_common.get_entrance_name(feature, entrance), \
                            feature.survey_county.survey_short_name, feature.survey_id, \
                            self.number, entrance.elevation_ft))

        self.number = self.number + 1


    def create_html_download_urls(self):
        return self.create_url('/mxf', 'Maptech (MXF)', get_mxf_filename(self.bulletin.id))


def get_mxf_filename(bulletin_id):
    return '%s/mxf/bulletin_%s.mxf' % (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)
