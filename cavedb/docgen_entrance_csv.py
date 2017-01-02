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

import csv
import cavedb.docgen_common
import cavedb.utils

class EntranceCsv(cavedb.docgen_common.Common):
    def __init__(self, bulletin):
        cavedb.docgen_common.Common.__init__(self, bulletin)
        self.csvfile = None
        self.csvwriter = None


    def open(self, all_regions_gis_hash):
        filename = get_csv_filename(self.bulletin.id)
        cavedb.docgen_common.create_base_directory(filename)
        self.csvfile = open(filename, 'w')
        self.csvwriter = csv.writer(self.csvfile, delimiter=',')

        self.csvwriter.writerow(['internal_id', 'locid', 'survey_prefix', 'survey_suffix',
                                 'survey_id', 'name', 'alternate_names', 'type', 'coord_acquision',
                                 'wgs84_lon', 'wgs84_lat', 'nad27_utmzone', 'nad27_utmeast',
                                 'nad27_utmnorth', 'elevation', 'region', 'county', 'quad',
                                 'length', 'depth', 'length_based_on', 'significant',
                                 'access enum', 'access descr', 'todo enum', 'todo descr',
                                 'source', 'gislbl_pri'])


    def feature_entrance(self, feature, entrance, coordinates):
        name = cavedb.docgen_common.get_entrance_name(feature, entrance)

        if feature.is_significant:
            gislbl_pri = 10
        elif feature.feature_type == 'FRO':
            gislbl_pri = 6
        else:
            gislbl_pri = 8

        self.csvwriter.writerow([feature.id, entrance.id, feature.survey_county.survey_short_name,
                                 feature.survey_id,
                                 feature.survey_county.survey_short_name + feature.survey_id,
                                 name, feature.alternate_names, feature.feature_type,
                                 entrance.coord_acquision, coordinates.wgs84_lon,
                                 coordinates.wgs84_lat, coordinates.utmzone,
                                 coordinates.nad27_utmeast, coordinates.nad27_utmnorth,
                                 entrance.elevation_ft, feature.bulletin_region.region_name,
                                 feature.survey_county.county_name,
                                 entrance.quad.quad_name if entrance.quad else '',
                                 feature.length_ft, feature.depth_ft, feature.length_based_on,
                                 feature.is_significant, feature.access_enum, feature.access_descr,
                                 feature.todo_enum, feature.todo_descr, feature.source, gislbl_pri])


    def close(self):
        self.csvfile.close()


    def create_html_download_urls(self):
        return self.create_url('/csv', 'Spreadsheet (CSV)', get_csv_filename(self.bulletin.id))


def get_csv_filename(bulletin_id):
    return '%s/csv/bulletin_%s.csv' % (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)
