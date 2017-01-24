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

from django.conf.urls import url, include
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.conf import settings

#pylint: disable=unused-argument
def forward_to_admin(request):
    return HttpResponseRedirect('/admin/')

admin.site.site_header = settings.ADMIN_SITE_HEADER

admin.autodiscover()

#pylint: disable=line-too-long
urlpatterns = [
    url(r'^$', forward_to_admin),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/generate$',
        'cavedb.generate_docs.generate_bulletin'),

    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/map/(?P<map_name>[\w\d\._-]+)$',
        'cavedb.views.show_all_regions_gis_map'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/region/(?P<region_id>\d+)/map/(?P<map_name>[\w\d\._-]+)$',
        'cavedb.views.show_region_gis_map'),

    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/pdf$', 'cavedb.views.show_pdf'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/color_pdf$', 'cavedb.views.show_color_pdf'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/draft_pdf$', 'cavedb.views.show_draft_pdf'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/todo$', 'cavedb.views.show_todo_txt'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/kml$', 'cavedb.views.show_kml'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/text$', 'cavedb.views.show_text'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/gpx$', 'cavedb.views.show_gpx'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/csv$', 'cavedb.views.show_csv'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/mxf$', 'cavedb.views.show_mxf'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/shp$', 'cavedb.views.show_shp'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/dvd$', 'cavedb.views.show_dvd'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/log$', 'cavedb.views.show_log'),

    url(r'^cavedb/bulletin_attachments/(?P<bulletin_id>\d+)/cover/(?P<filename>[\w\d\s\&\._-]+)$',
        'cavedb.views.show_bulletin_cover'),
    url(r'^cavedb/bulletin_attachments/(?P<bulletin_id>\d+)/attachments/(?P<filename>[\w\d\s\&\._-]+)$',
        'cavedb.views.show_bulletin_attachment'),
    url(r'^cavedb/bulletin_attachments/(?P<bulletin_id>\d+)/gis_lineplot/(?P<filename>[\w\d\s\&\._-]+)$',
        'cavedb.views.show_bulletin_gis_lineplot'),

    url(r'^cavedb/feature_attachments/(?P<feature_id>\d+)/photos/(?P<filename>[\w\d\s\&\._-]+)$',
        'cavedb.views.show_feature_photo'),
    url(r'^cavedb/feature_attachments/(?P<feature_id>\d+)/attachments/(?P<filename>[\w\d\s\&\._-]+)$',
        'cavedb.views.show_feature_attachment'),
    url(r'^cavedb/feature_attachments/(?P<feature_id>\d+)/gis_lineplot/(?P<filename>[\w\d\s\&\._-]+)$',
        'cavedb.views.show_feature_gis_lineplot'),
]

