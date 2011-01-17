from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to
from jsonrpc import jsonrpc_site
from jsonrpc.views import browse as json_browse

import exeapp.views.handlers.package_rpc
import exeapp.views.main


from exeapp.views import main

urlpatterns = patterns('',
            # (r'', 'exeapp.views.main'),
            (r'^$', main.main),
            
            url(r'^json/$', jsonrpc_site.dispatch, name="jsonrpc_mountpoint"),
            (r'package/$', redirect_to, {'url' : '/exeapp/'}),
            (r'package/(?P<package_id>\d+)/', include('exeapp.package_urls')),
        )

if settings.DEBUG:
    urlpatterns += patterns('',
            url(r'^json/browse/', json_browse, name='jsonrpc_browser'),
        )