from django.conf.urls.defaults import *

from cavedb.views import forward_to_admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^cavedb/', include('cavedb.urls')),
    (r'^$', forward_to_admin),
)
