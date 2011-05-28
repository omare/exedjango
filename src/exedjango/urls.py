from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': '/exeapp/'}),
    (r'tinymce/', include('tinymce.urls')),
    (r'^exeapp/', include('exeapp.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('exedjango.accountsurl')),
    
)

