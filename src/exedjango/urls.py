from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': '/exeapp/'}),
    (r'^exeapp/', include('exeapp.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('exedjango.accountsurl')),
)
