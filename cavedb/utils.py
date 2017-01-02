# Copyright 2007-2016 Brian Masney <masneyb@onstation.org>
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

import math
from os.path import getsize
import re
import datetime
import dateutil.parser
import dateutil.relativedelta
import cavedb.settings

def get_bulletin_base_dir(bulletin_id):
    return '%s/bulletins/bulletin_%s' % (cavedb.settings.MEDIA_ROOT, bulletin_id)


def get_build_script(bulletin_id):
    return '%s/dobuild' % (get_bulletin_base_dir(bulletin_id))


def get_build_script_wrapper(bulletin_id):
    return '%s/build' % (get_bulletin_base_dir(bulletin_id))


def get_build_lock_file(bulletin_id):
    return '%s/build-in-progress.lock' % (get_bulletin_base_dir(bulletin_id))


def get_build_log_filename(bulletin_id):
    return '%s/bulletin-build-output.txt' % (get_bulletin_base_dir(bulletin_id))


def get_output_base_dir(bulletin_id):
    return '%s/output' % (get_bulletin_base_dir(bulletin_id))


def get_color_tex_filename(bulletin_id):
    return '%s/pdf_color/bulletin_%s.tex' % (get_output_base_dir(bulletin_id), bulletin_id)


def get_bw_tex_filename(bulletin_id):
    return '%s/pdf_bw/bulletin_%s.tex' % (get_output_base_dir(bulletin_id), bulletin_id)


def get_draft_tex_filename(bulletin_id):
    return '%s/pdf_draft/bulletin_%s.tex' % (get_output_base_dir(bulletin_id), bulletin_id)


def get_pdf_filename(bulletin_id):
    return '%s/pdf_bw/bulletin_%s.pdf' % (get_output_base_dir(bulletin_id), bulletin_id)


def get_color_pdf_filename(bulletin_id):
    return '%s/pdf_color/bulletin_%s.pdf' % (get_output_base_dir(bulletin_id), bulletin_id)


def get_draft_pdf_filename(bulletin_id):
    return '%s/pdf_draft/bulletin_%s.pdf' % (get_output_base_dir(bulletin_id), bulletin_id)


def get_todo_txt_filename(bulletin_id):
    return '%s/todo/bulletin_%s_todo.txt' % (get_output_base_dir(bulletin_id), bulletin_id)


def get_kml_filename(bulletin_id):
    return '%s/kml/bulletin_%s.kml' % (get_output_base_dir(bulletin_id), bulletin_id)


def get_text_filename(bulletin_id):
    return '%s/text/bulletin_%s.txt' % (get_output_base_dir(bulletin_id), bulletin_id)


def get_gpx_filename(bulletin_id):
    return '%s/gpx/bulletin_%s.gpx' % (get_output_base_dir(bulletin_id), bulletin_id)


def get_csv_filename(bulletin_id):
    return '%s/csv/bulletin_%s.csv' % (get_output_base_dir(bulletin_id), bulletin_id)


def get_mxf_filename(bulletin_id):
    return '%s/mxf/bulletin_%s.mxf' % (get_output_base_dir(bulletin_id), bulletin_id)


def get_gis_maps_directory(bulletin_id):
    return '%s/gis_maps' % (get_output_base_dir(bulletin_id))


def get_mapserver_mapfile(bulletin_id, map_name):
    return '%s/%s.map' % (get_gis_maps_directory(bulletin_id), map_name)


def get_mapserver_fonts_list(bulletin_id):
    return '%s/fonts.list' % (get_gis_maps_directory(bulletin_id))


def get_all_regions_gis_map(bulletin_id, map_name):
    return '%s/bulletin_%s_gis_%s_map.jpg' % \
           (get_gis_maps_directory(bulletin_id), bulletin_id, map_name)


def get_region_gis_map(bulletin_id, region_id, map_name):
    return '%s/bulletin_%s_region_%s_gis_%s_map.jpg' % \
           (get_gis_maps_directory(bulletin_id), bulletin_id, region_id, map_name)


LOCATIONS_SHP_LAYER_NAME = 'karst_feature_locations'
REGION_EXTENTS_SHP_LAYER_NAME = 'region_extents'


def get_shp_directory(bulletin_id):
    return '%s/shp' % (get_output_base_dir(bulletin_id))


def get_shp_zip_filename(bulletin_id):
    return '%s/%s.zip' % (get_shp_directory(bulletin_id), LOCATIONS_SHP_LAYER_NAME)


def get_dvd_filename(bulletin_id):
    return '%s/dvd.zip' % (get_output_base_dir(bulletin_id))


def get_file_size(filename):
    try:
        size = getsize(filename)
        if size is 0:
            return 0
    except OSError:
        return 'UNKNOWN'

    i = math.floor(math.log(size, 1024))
    return ("%.1f %s" % (size / math.pow(1024, i), ['bytes', 'KB', 'MB', 'GB', 'TB'][int(i)])) \
               .replace('.0 ', ' ')


def comma_split(inputstr):
    return split_strip(inputstr, ',', [])


def newline_split(inputstr):
    return split_strip(inputstr, '\n', ['\r'])


def split_strip(inputstr, separator, chars_to_strip):
    ret = []

    if not inputstr:
        return ret

    for member in inputstr.split(separator):
        member = member.strip()
        for char in chars_to_strip:
            member = member.replace(char, '')
        if not member:
            continue

        ret.append(member)

    return ret


def get_all_feature_alt_names(feature):
    alternate_names = comma_split(feature.alternate_names)
    additional_index_names = comma_split(feature.additional_index_names)

    return alternate_names + additional_index_names


def get_normalized_date(datestr):
    # Parse different date formats including:
    # Sep 21, 1997, Fall/Winter 1997, Fall 1997, etc.

    if not datestr:
        return "0000-00-00"

    pattern = re.compile(r'/[\w\d]+')
    datestr = pattern.sub('', datestr)

    datestr = datestr.replace("Spring", "April")
    datestr = datestr.replace("Summer", "July")
    datestr = datestr.replace("Fall", "October")
    datestr = datestr.replace("Winter", "January")

    try:
        defaults = datetime.datetime.now() + \
                   dateutil.relativedelta.relativedelta(month=1, day=1, hour=0, minute=0, \
                                                        second=0, microsecond=0)
        return dateutil.parser.parse(datestr, default=defaults).strftime("%Y-%m-%d")
    except ValueError:
        return "0000-00-00"

