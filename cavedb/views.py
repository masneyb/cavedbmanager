# Copyright 2007-2017 Brian Masney <masneyb@onstation.org>
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

import sys
from mimetypes import guess_type
from time import strftime
from os.path import isfile, getsize
from curses.ascii import isalpha
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponseRedirect, HttpResponse, Http404
from cavedb import settings
import cavedb.docgen_common
import cavedb.docgen_dvd
import cavedb.docgen_entrance_csv
import cavedb.docgen_gis_maps
import cavedb.docgen_gpx
import cavedb.docgen_kml
import cavedb.docgen_latex_letter_bw
import cavedb.docgen_latex_letter_color
import cavedb.docgen_latex_letter_draft
import cavedb.docgen_mxf
import cavedb.docgen_shp
import cavedb.docgen_text
import cavedb.docgen_todo_txt
import cavedb.models
import cavedb.perms
import cavedb.utils

def show_pdf(request, bulletin_id):
    localfile = cavedb.docgen_latex_letter_bw.get_pdf_filename(bulletin_id)
    remotefile = get_bulletin_remote_file(bulletin_id, 'pdf')
    return do_show_bulletin_attachment(request, bulletin_id, localfile, remotefile)


def show_color_pdf(request, bulletin_id):
    localfile = cavedb.docgen_latex_letter_color.get_color_pdf_filename(bulletin_id)
    remotefile = '%s_color.pdf' % (get_bulletin_base_name(bulletin_id))
    return do_show_bulletin_attachment(request, bulletin_id, localfile, remotefile)


def show_draft_pdf(request, bulletin_id):
    localfile = cavedb.docgen_latex_letter_draft.get_draft_pdf_filename(bulletin_id)
    remotefile = '%s_draft.pdf' % (get_bulletin_base_name(bulletin_id))
    return do_show_bulletin_attachment(request, bulletin_id, localfile, remotefile)


def show_todo_txt(request, bulletin_id):
    localfile = cavedb.docgen_todo_txt.get_todo_txt_filename(bulletin_id)
    remotefile = '%s_todo.txt' % (get_bulletin_base_name(bulletin_id))
    return do_show_bulletin_attachment(request, bulletin_id, localfile, remotefile)


def show_kml(request, bulletin_id):
    localfile = cavedb.docgen_kml.get_bulletin_kml_filename(bulletin_id)
    remotefile = get_bulletin_remote_file(bulletin_id, 'kml')
    return do_show_bulletin_attachment(request, bulletin_id, localfile, remotefile)


def show_text(request, bulletin_id):
    localfile = cavedb.docgen_text.get_text_filename(bulletin_id)
    remotefile = get_bulletin_remote_file(bulletin_id, 'txt')
    return do_show_bulletin_attachment(request, bulletin_id, localfile, remotefile)


def show_gpx(request, bulletin_id):
    localfile = cavedb.docgen_gpx.get_bulletin_gpx_filename(bulletin_id)
    remotefile = get_bulletin_remote_file(bulletin_id, 'gpx')
    return do_show_bulletin_attachment(request, bulletin_id, localfile, remotefile)


def show_csv(request, bulletin_id):
    localfile = cavedb.docgen_entrance_csv.get_bulletin_csv_filename(bulletin_id)
    remotefile = get_bulletin_remote_file(bulletin_id, 'csv')
    return do_show_bulletin_attachment(request, bulletin_id, localfile, remotefile)


def show_mxf(request, bulletin_id):
    localfile = cavedb.docgen_mxf.get_bulletin_mxf_filename(bulletin_id)
    remotefile = get_bulletin_remote_file(bulletin_id, 'mxf')
    return do_show_bulletin_attachment(request, bulletin_id, localfile, remotefile)


def show_shp(request, bulletin_id):
    localfile = cavedb.docgen_shp.get_bulletin_shp_zip_filename(bulletin_id)
    remotefile = '%s_shp_files.zip' % (get_bulletin_base_name(bulletin_id))
    return do_show_bulletin_attachment(request, bulletin_id, localfile, remotefile)


def show_dvd(request, bulletin_id):
    localfile = cavedb.docgen_dvd.get_bulletin_dvd_filename(bulletin_id)
    remotefile = get_bulletin_remote_file(bulletin_id, 'zip')
    return do_show_bulletin_attachment(request, bulletin_id, localfile, remotefile)


def show_log(request, bulletin_id):
    localfile = cavedb.utils.get_build_log_filename(bulletin_id)
    remotefile = get_bulletin_remote_file(bulletin_id, 'txt')
    return do_show_bulletin_attachment(request, bulletin_id, localfile, remotefile)


def show_all_regions_gis_map(request, bulletin_id, map_name):
    localfile = cavedb.docgen_gis_maps.get_all_regions_gis_map(bulletin_id, map_name)
    return do_show_bulletin_attachment(request, bulletin_id, localfile, None)


def show_region_gis_map(request, bulletin_id, region_id, map_name):
    localfile = cavedb.docgen_gis_maps.get_region_gis_map(bulletin_id, region_id, map_name)
    return do_show_bulletin_attachment(request, bulletin_id, localfile, None)


def show_bulletin_cover(request, bulletin_id, filename):
    localfile = '%s/bulletin_attachments/%s/cover/%s' % (settings.MEDIA_ROOT, bulletin_id, filename)
    return do_show_bulletin_attachment(request, bulletin_id, localfile, filename)


def show_bulletin_attachment(request, bulletin_id, filename):
    localfile = '%s/bulletin_attachments/%s/attachments/%s' % \
                    (settings.MEDIA_ROOT, bulletin_id, filename)
    return do_show_bulletin_attachment(request, bulletin_id, localfile, filename)


def show_bulletin_gis_lineplot(request, bulletin_id, filename):
    localfile = '%s/bulletin_attachments/%s/gis_lineplot/%s' % \
                    (settings.MEDIA_ROOT, bulletin_id, filename)
    return do_show_bulletin_attachment(request, bulletin_id, localfile, filename)


def get_feature_bulletin_id(feature_id):
    features = cavedb.models.Feature.objects.filter(id=feature_id)
    if features.count() == 0:
        raise Http404

    return features[0].bulletin_region.bulletin.id


def show_feature_photo(request, feature_id, filename):
    localfile = '%s/feature_attachments/%s/photos/%s' % (settings.MEDIA_ROOT, feature_id, filename)
    return do_show_bulletin_attachment(request, \
               get_feature_bulletin_id(feature_id), localfile, filename)


def show_feature_attachment(request, feature_id, filename):
    localfile = '%s/feature_attachments/%s/attachments/%s' % \
                    (settings.MEDIA_ROOT, feature_id, filename)
    return do_show_bulletin_attachment(request, \
               get_feature_bulletin_id(feature_id), localfile, filename)


def show_feature_gis_lineplot(request, feature_id, filename):
    localfile = '%s/feature_attachments/%s/gis_lineplot/%s' % \
                    (settings.MEDIA_ROOT, feature_id, filename)
    return do_show_bulletin_attachment(request, \
               get_feature_bulletin_id(feature_id), localfile, filename)


def do_show_bulletin_attachment(request, bulletin_id, localfile, remotefile):
    #pylint: disable=unused-argument
    if not cavedb.perms.is_bulletin_allowed(bulletin_id):
        raise Http404

    if not isfile(localfile):
        raise Http404

    mimetype = guess_type(localfile)[0]
    if mimetype is None:
        mimetype = "application/octet-stream"

    try:
        wrapper = FileWrapper(file(localfile))
        response = HttpResponse(wrapper, content_type=mimetype)

        if remotefile and (mimetype is None or not mimetype.startswith('image')):
            response['Content-Disposition'] = 'attachment; filename=' + remotefile

        response['Content-Length'] = getsize(localfile)
    except IOError:
        print >> sys.stderr, 'Cannot find %s\n' % (localfile)
        raise Http404

    return response


def get_bulletin_base_name(bulletin_id):
    bulletins = cavedb.models.Bulletin.objects.filter(id=bulletin_id)
    if bulletins.count() == 0:
        raise Http404

    base = ''
    for char in bulletins[0].short_name.lower().encode('ascii'):
        if isalpha(char):
            base += char
        else:
            base += '_'

    if base == '':
        base = 'bulletin_%s' % (bulletin_id)

    mtime = bulletins[0].get_bulletin_mod_date()
    if mtime != None:
        disp_date = strftime("%Y%m%d-%H%M%S", mtime)
    else:
        disp_date = "UNKNOWN"

    return '%s_%s' % (base, disp_date)


def get_bulletin_remote_file(bulletin_id, extension):
    return '%s.%s' % (get_bulletin_base_name(bulletin_id), extension)


def generate_bulletin(request, bulletin_id):
    #pylint: disable=unused-argument
    if not cavedb.perms.is_bulletin_generation_allowed(bulletin_id):
        raise Http404

    bulletin = cavedb.models.Bulletin.objects.get(pk=bulletin_id)
    if bulletin is None:
        raise Http404

    build_lock_file = cavedb.utils.get_build_lock_file(bulletin_id)
    cavedb.docgen_common.create_base_directory(build_lock_file)
    with open(build_lock_file, 'w') as output:
        output.write('')

    settings.QUEUE_STRATEGY(bulletin_id)

    return HttpResponseRedirect('%sadmin/cavedb/bulletin/' % (settings.CONTEXT_PATH))
