from django.conf.urls.defaults import *

from exeapp.views.package_rpc import *

urlpatterns = patterns('exeapp.views',
                       (r'^$', 'package.package'),
                       (r'authoring/', 'package.authoring'),
                       (r'properties/', 'package.properties'))