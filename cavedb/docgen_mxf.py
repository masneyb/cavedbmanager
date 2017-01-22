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
import cavedb.utils

class Mxf(cavedb.docgen_common.Common):
    def __init__(self, filename, download_url):
        cavedb.docgen_common.Common.__init__(self)
        self.filename = filename
        self.download_url = download_url
        self.number = 1
        self.mxffile = None


    def open(self, all_regions_gis_hash):
        cavedb.docgen_common.create_base_directory(self.filename)
        self.mxffile = open(self.filename, 'w')


    def close(self):
        self.mxffile.close()


    def feature_entrance(self, feature, entrance, coordinates):
        wgs84_lon_lat = coordinates.get_lon_lat_wgs84()

        self.mxffile.write('%s, %s, \"%s\", \"%s%s\", \"Number: %s Height: %s\", ff0000, 3\n' % \
                           (wgs84_lon_lat[1], wgs84_lon_lat[0], \
                            cavedb.docgen_common.get_entrance_name(feature, entrance), \
                            feature.survey_county.survey_short_name, feature.survey_id, \
                            self.number, entrance.elevation_ft))

        self.number = self.number + 1


    def create_html_download_urls(self):
        return self.create_url(self.download_url, 'Maptech (MXF)', self.filename)


def create_for_bulletin(bulletin):
    return Mxf(get_bulletin_mxf_filename(bulletin.id), 'bulletin/%s/mxf' % (bulletin.id))


def create_for_global():
    return Mxf(get_global_mxf_filename(), None)


def get_bulletin_mxf_filename(bulletin_id):
    return '%s/mxf/bulletin_%s.mxf' % (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)


def get_global_mxf_filename():
    return '%s/mxf/all.mxf' % (cavedb.utils.get_global_output_base_dir())
