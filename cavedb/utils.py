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
from mimetypes import guess_type
from os.path import getsize
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.http import Http404
from cavedb.middleware import get_current_user

def send_file(localfile, remotefile):
    # FIXME - Find out how the file transfer can be streamed

    try:
        filed = open(localfile, 'r')
        output = filed.read()
        filed.close()
    except IOError:
        raise Http404

    mimetype = guess_type(localfile)[0]
    if mimetype is None:
        mimetype = "application/octet-stream"

    response = HttpResponse(output, content_type=mimetype)
    if remotefile and (mimetype is None or not mimetype.startswith('image')):
        response['Content-Disposition'] = 'attachment; filename=' + remotefile

    response['Content-Length'] = getsize(localfile)

    return response


def get_pdf_filename(bulletin_id):
    return '%s/bulletins/bulletin_%s/output/pdf_bw/bulletin_%s.pdf' % \
               (settings.MEDIA_ROOT, bulletin_id, bulletin_id)


def get_color_pdf_filename(bulletin_id):
    return '%s/bulletins/bulletin_%s/output/pdf_color/bulletin_%s.pdf' % \
               (settings.MEDIA_ROOT, bulletin_id, bulletin_id)


def get_draft_pdf_filename(bulletin_id):
    return '%s/bulletins/bulletin_%s/output/pdf_draft/bulletin_%s.pdf' % \
               (settings.MEDIA_ROOT, bulletin_id, bulletin_id)


def get_todo_pdf_filename(bulletin_id):
    return '%s/bulletins/bulletin_%s/output/todo/bulletin_%s_todo.pdf' % \
               (settings.MEDIA_ROOT, bulletin_id, bulletin_id)


def get_kml_filename(bulletin_id):
    return '%s/bulletins/bulletin_%s/output/kml/bulletin_%s.kml' % \
               (settings.MEDIA_ROOT, bulletin_id, bulletin_id)


def get_text_filename(bulletin_id):
    return '%s/bulletins/bulletin_%s/output/text/bulletin_%s.txt' % \
               (settings.MEDIA_ROOT, bulletin_id, bulletin_id)


def get_gpx_filename(bulletin_id):
    return '%s/bulletins/bulletin_%s/output/gpx/bulletin_%s.gpx' % \
               (settings.MEDIA_ROOT, bulletin_id, bulletin_id)


def get_csv_filename(bulletin_id):
    return '%s/bulletins/bulletin_%s/output/csv/bulletin_%s.csv' % \
               (settings.MEDIA_ROOT, bulletin_id, bulletin_id)


def get_mxf_filename(bulletin_id):
    return '%s/bulletins/bulletin_%s/output/mxf/bulletin_%s.mxf' % \
               (settings.MEDIA_ROOT, bulletin_id, bulletin_id)


def get_shp_filename(bulletin_id):
    return '%s/bulletins/bulletin_%s/output/shp/karst_feature_locations.zip' % \
               (settings.MEDIA_ROOT, bulletin_id)


def get_xml_filename(bulletin_id):
    return '%s/bulletins/bulletin_%s/output/bulletin_%s.xml' % \
               (settings.MEDIA_ROOT, bulletin_id, bulletin_id)


def get_dvd_filename(bulletin_id):
    return '%s/bulletins/bulletin_%s/output/dvd/dvd.zip' % \
               (settings.MEDIA_ROOT, bulletin_id)


def get_build_log_filename(bulletin_id):
    return '%s/bulletins/bulletin_%s/bulletin-build-output.txt' % \
               (settings.MEDIA_ROOT, bulletin_id)


def is_bulletin_generation_allowed(bulletin_id):
    if isinstance(get_current_user(), AnonymousUser):
        return False

    profile = get_current_user().caveuserprofile
    return profile.can_generate_docs and \
               profile.bulletins.get_queryset().filter(id=bulletin_id).count() > 0


def is_bulletin_docs_allowed(bulletin_id):
    if isinstance(get_current_user(), AnonymousUser):
        return False

    profile = get_current_user().caveuserprofile
    return profile.can_download_docs and \
               profile.bulletins.get_queryset().filter(id=bulletin_id).count() > 0


def is_bulletin_gis_maps_allowed(bulletin_id):
    if isinstance(get_current_user(), AnonymousUser):
        return False

    profile = get_current_user().caveuserprofile
    return profile.can_download_gis_maps and \
               profile.bulletins.get_queryset().filter(id=bulletin_id).count() > 0


def is_bulletin_allowed(bulletin_id):
    if isinstance(get_current_user(), AnonymousUser):
        return False

    return get_current_user() \
               .caveuserprofile \
               .bulletins \
               .get_queryset() \
               .filter(id=bulletin_id) \
               .count() > 0


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

