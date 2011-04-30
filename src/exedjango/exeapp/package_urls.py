from django.conf.urls.defaults import *

# have to import rpc views manually
# from exeapp.views.package_outline_rpc import *

urlpatterns = patterns('exeapp.views',
                       (r'^$', 'package.package'),
                       (r'authoring/$', 'package.authoring'),
                       (r'authoring/handle_action/$', 'package.handle_action'),
                       (r'properties/$', 'package.properties'),
                       (r'download/(?P<format>\w+)/$', 'package.export'),
                       )