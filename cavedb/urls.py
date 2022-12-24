# SPDX-License-Identifier: Apache-2.0

from django.urls import re_path
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.conf import settings
import cavedb.views

#pylint: disable=unused-argument
def forward_to_admin(request):
    return HttpResponseRedirect('/admin/')

admin.site.site_header = settings.ADMIN_SITE_HEADER

admin.autodiscover()

#pylint: disable=line-too-long
urlpatterns = [
    re_path(r'^$', forward_to_admin),
    re_path(r'^admin/', admin.site.urls),

    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/generate$',
            cavedb.views.generate_bulletin),

    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/map/(?P<map_name>[\w\d\._-]+)$',
            cavedb.views.show_all_regions_gis_map),
    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/region/(?P<region_id>\d+)/map/(?P<map_name>[\w\d\._-]+)$',
            cavedb.views.show_region_gis_map),

    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/pdf$', cavedb.views.show_pdf),
    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/color_pdf$', cavedb.views.show_color_pdf),
    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/draft_pdf$', cavedb.views.show_draft_pdf),
    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/todo$', cavedb.views.show_todo_txt),
    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/kml$', cavedb.views.show_kml),
    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/text$', cavedb.views.show_text),
    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/gpx$', cavedb.views.show_gpx),
    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/csv$', cavedb.views.show_csv),
    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/mxf$', cavedb.views.show_mxf),
    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/shp$', cavedb.views.show_shp),
    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/dvd$', cavedb.views.show_dvd),
    re_path(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/log$', cavedb.views.show_log),

    re_path(r'^cavedb/statewide_docs/(?P<doc_type>\d+)/(?P<filename>[\w\d\s\&\._-]+)$',
            cavedb.views.show_statewide_doc),

    re_path(r'^cavedb/bulletin_attachments/(?P<bulletin_id>\d+)/cover/(?P<filename>[\w\d\s\&\._-]+)$',
            cavedb.views.show_bulletin_cover),
    re_path(r'^cavedb/bulletin_attachments/(?P<bulletin_id>\d+)/attachments/(?P<filename>[\w\d\s\&\._-]+)$',
            cavedb.views.show_bulletin_attachment),
    re_path(r'^cavedb/bulletin_attachments/(?P<bulletin_id>\d+)/gis_lineplot/(?P<filename>[\w\d\s\&\._-]+)$',
            cavedb.views.show_bulletin_gis_lineplot),

    re_path(r'^cavedb/feature_attachments/(?P<feature_id>\d+)/photos/(?P<filename>[\w\d\s\&\._-]+)$',
            cavedb.views.show_feature_photo),
    re_path(r'^cavedb/feature_attachments/(?P<feature_id>\d+)/attachments/(?P<filename>[\w\d\s\&\._-]+)$',
            cavedb.views.show_feature_attachment),
    re_path(r'^cavedb/feature_attachments/(?P<feature_id>\d+)/gis_lineplot/(?P<filename>[\w\d\s\&\._-]+)$',
            cavedb.views.show_feature_gis_lineplot),
]
