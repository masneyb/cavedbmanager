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

