# SPDX-License-Identifier: Apache-2.0

import csv
import cavedb.docgen_common
import cavedb.utils

class EntranceCsv(cavedb.docgen_common.Common):
    def __init__(self, filename, download_url):
        cavedb.docgen_common.Common.__init__(self)
        self.filename = filename
        self.download_url = download_url
        self.csvfile = None
        self.csvwriter = None


    def open(self, all_regions_gis_hash):
        # pylint: disable=consider-using-with
        cavedb.docgen_common.create_base_directory(self.filename)
        self.csvfile = open(self.filename, 'w', encoding='utf-8')
        self.csvwriter = csv.writer(self.csvfile, delimiter=',')

        self.csvwriter.writerow(['internal_id', 'locid', 'survey_id', 'name', 'alternate_names',
                                 'type', 'coord_acquision', 'wgs84_lon', 'wgs84_lat',
                                 'nad83_utmzone', 'nad83_utmeast', 'nad83_utmnorth', 'elevation',
                                 'region', 'county', 'quad', 'length', 'depth', 'length_based_on',
                                 'significant', 'access enum', 'access descr', 'todo enum',
                                 'todo descr', 'source', 'gislbl_pri'])


    def feature_entrance(self, feature, entrance, coordinates):
        name = cavedb.docgen_common.get_entrance_name(feature, entrance)

        if feature.is_significant:
            gislbl_pri = 10
        elif feature.feature_type == 'FRO':
            gislbl_pri = 6
        else:
            gislbl_pri = 8

        lon_lat_wgs84 = coordinates.get_lon_lat_wgs84()
        utm_nad83 = coordinates.get_utm_nad83()

        if feature.survey_id:
            survey_id = feature.survey_county.survey_short_name + feature.survey_id
        else:
            survey_id = ""

        self.csvwriter.writerow([feature.id, entrance.id, survey_id,
                                 name, feature.alternate_names, feature.feature_type,
                                 entrance.coord_acquision, lon_lat_wgs84[0],
                                 lon_lat_wgs84[1], entrance.utmzone, utm_nad83[0], utm_nad83[1],
                                 entrance.elevation_ft, feature.bulletin_region.region_name,
                                 feature.survey_county.county_name,
                                 entrance.quad.quad_name if entrance.quad else '',
                                 feature.length_ft, feature.depth_ft, feature.length_based_on,
                                 feature.is_significant, feature.access_enum, feature.access_descr,
                                 feature.todo_enum, feature.todo_descr, feature.source,
                                 gislbl_pri])

    def close(self):
        self.csvfile.close()


    def create_html_download_urls(self):
        return self.create_url(self.download_url, 'Spreadsheet (CSV)', self.filename)


def create_for_bulletin(bulletin):
    return EntranceCsv(get_bulletin_csv_filename(bulletin.id), \
                       'bulletin/%s/csv' % (bulletin.id))


def create_for_global():
    return EntranceCsv(get_global_csv_filename(), None)


def get_bulletin_csv_filename(bulletin_id):
    return '%s/csv/bulletin_%s.csv' % (cavedb.utils.get_output_base_dir(bulletin_id), bulletin_id)


def get_global_csv_filename():
    return '%s/csv/all.csv' % (cavedb.utils.get_global_output_base_dir())
