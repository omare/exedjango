from django.conf.urls.defaults import *
from django.http import HttpResponseRedirect
from django.conf import settings
from django.views.generic.simple import redirect_to
from django.views.static import serve

urlpatterns = patterns('',
            # (r'', 'exeapp.views.main'),
            (r'main/$', 'exeapp.views.main.main'),
            (r'createpackage', 'exeapp.views.main.create_package'),
            (r'package/$', redirect_to, {'url' : '/exeapp/main/'}),
            (r'package/(?P<package_id>\d+)/$', 'exeapp.views.package.package'),
        )

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 
            'django.views.static.serve', 
            {'document_root' : settings.STATIC_ROOT}))