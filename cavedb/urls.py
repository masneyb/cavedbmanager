from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^bulletin/(?P<bulletin_id>\d+)/generate$', 'cavedb.views.generate_bulletin'),

    (r'^bulletin/(?P<bulletin_id>\d+)/region/(?P<region_id>\d+)/topo_map$', 'cavedb.views.show_region_topo_gis_map'),
    (r'^bulletin/(?P<bulletin_id>\d+)/region/(?P<region_id>\d+)/aerial_map/(?P<aerial_map_name>[\w\d\._-]+)$', 'cavedb.views.show_region_aerial_gis_map'),

    (r'^bulletin/(?P<bulletin_id>\d+)/pdf$', 'cavedb.views.show_pdf'),
    (r'^bulletin/(?P<bulletin_id>\d+)/color_pdf$', 'cavedb.views.show_color_pdf'),
    (r'^bulletin/(?P<bulletin_id>\d+)/draft_pdf$', 'cavedb.views.show_draft_pdf'),
    (r'^bulletin/(?P<bulletin_id>\d+)/todo_pdf$', 'cavedb.views.show_todo_pdf'),
    (r'^bulletin/(?P<bulletin_id>\d+)/kml$', 'cavedb.views.show_kml'),
    (r'^bulletin/(?P<bulletin_id>\d+)/text$', 'cavedb.views.show_text'),
    (r'^bulletin/(?P<bulletin_id>\d+)/gpx$', 'cavedb.views.show_gpx'),
    (r'^bulletin/(?P<bulletin_id>\d+)/csv$', 'cavedb.views.show_csv'),
    (r'^bulletin/(?P<bulletin_id>\d+)/mxf$', 'cavedb.views.show_mxf'),
    (r'^bulletin/(?P<bulletin_id>\d+)/shp$', 'cavedb.views.show_shp'),
    (r'^bulletin/(?P<bulletin_id>\d+)/xml$', 'cavedb.views.show_xml'),
    (r'^bulletin/(?P<bulletin_id>\d+)/dvd$', 'cavedb.views.show_dvd'),
    (r'^bulletin/(?P<bulletin_id>\d+)/log$', 'cavedb.views.show_log'),

    (r'^bulletin_attachments/(?P<bulletin_id>\d+)/cover/(?P<filename>[\w\d\s\&\._-]+)$', 'cavedb.views.show_bulletin_cover'),
    (r'^bulletin_attachments/(?P<bulletin_id>\d+)/attachments/(?P<filename>[\w\d\s\&\._-]+)$', 'cavedb.views.show_bulletin_attachment'),
    (r'^bulletin_attachments/(?P<bulletin_id>\d+)/gis_lineplot/(?P<filename>[\w\d\s\&\._-]+)$', 'cavedb.views.show_bulletin_gis_lineplot'),

    (r'^feature_attachments/(?P<feature_id>\d+)/photos/(?P<filename>[\w\d\s\&\._-]+)$', 'cavedb.views.show_feature_photo'),
    (r'^feature_attachments/(?P<feature_id>\d+)/attachments/(?P<filename>[\w\d\s\&\._-]+)$', 'cavedb.views.show_feature_attachment'),
    (r'^feature_attachments/(?P<feature_id>\d+)/gis_lineplot/(?P<filename>[\w\d\s\&\._-]+)$', 'cavedb.views.show_feature_gis_lineplot'),
)
