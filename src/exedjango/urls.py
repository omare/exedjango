from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^$', redirect_to, {'url': '/exeapp/'}),
    (r'^exeapp/', include('exeapp.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('exedjango.accountsurl')),
)
