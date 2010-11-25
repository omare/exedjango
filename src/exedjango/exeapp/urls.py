from django.conf.urls.defaults import *
from django.http import HttpResponseRedirect
from django.conf import settings
from django.views.generic.simple import redirect_to
from django.views.static import serve

urlpatterns = patterns('exeapp.views',
            # (r'', 'exeapp.views.main'),
            (r'main/$', 'main.main'),
            (r'createpackage', 'main.create_package'),
            (r'package/$', redirect_to, {'url' : '/exeapp/main/'}),
            (r'package/(?P<package_id>\d+)/$', 'package.package'),
        )

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 
            'django.views.static.serve', 
            {'document_root' : settings.STATIC_ROOT}))