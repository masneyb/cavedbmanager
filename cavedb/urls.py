from django.conf.urls import patterns, url, include
from django.contrib import admin
from cavedb.views import forward_to_admin
from . import settings

admin.site.site_header = settings.ADMIN_SITE_HEADER

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', forward_to_admin),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/generate$', 'cavedb.views.generate_bulletin'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/generateXmlOnly$', 'cavedb.views.generate_xml_only_bulletin'),

    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/region/(?P<region_id>\d+)/topo_map$', 'cavedb.views.show_region_topo_gis_map'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/region/(?P<region_id>\d+)/aerial_map/(?P<aerial_map_name>[\w\d\._-]+)$', 'cavedb.views.show_region_aerial_gis_map'),

    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/pdf$', 'cavedb.views.show_pdf'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/color_pdf$', 'cavedb.views.show_color_pdf'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/draft_pdf$', 'cavedb.views.show_draft_pdf'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/todo_pdf$', 'cavedb.views.show_todo_pdf'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/kml$', 'cavedb.views.show_kml'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/text$', 'cavedb.views.show_text'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/gpx$', 'cavedb.views.show_gpx'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/csv$', 'cavedb.views.show_csv'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/mxf$', 'cavedb.views.show_mxf'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/shp$', 'cavedb.views.show_shp'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/xml$', 'cavedb.views.show_xml'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/dvd$', 'cavedb.views.show_dvd'),
    url(r'^cavedb/bulletin/(?P<bulletin_id>\d+)/log$', 'cavedb.views.show_log'),

    url(r'^cavedb/bulletin_attachments/(?P<bulletin_id>\d+)/cover/(?P<filename>[\w\d\s\&\._-]+)$', 'cavedb.views.show_bulletin_cover'),
    url(r'^cavedb/bulletin_attachments/(?P<bulletin_id>\d+)/attachments/(?P<filename>[\w\d\s\&\._-]+)$', 'cavedb.views.show_bulletin_attachment'),
    url(r'^cavedb/bulletin_attachments/(?P<bulletin_id>\d+)/gis_lineplot/(?P<filename>[\w\d\s\&\._-]+)$', 'cavedb.views.show_bulletin_gis_lineplot'),

    url(r'^cavedb/feature_attachments/(?P<feature_id>\d+)/photos/(?P<filename>[\w\d\s\&\._-]+)$', 'cavedb.views.show_feature_photo'),
    url(r'^cavedb/feature_attachments/(?P<feature_id>\d+)/attachments/(?P<filename>[\w\d\s\&\._-]+)$', 'cavedb.views.show_feature_attachment'),
    url(r'^cavedb/feature_attachments/(?P<feature_id>\d+)/gis_lineplot/(?P<filename>[\w\d\s\&\._-]+)$', 'cavedb.views.show_feature_gis_lineplot'),
)
