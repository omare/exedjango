from django.conf.urls.defaults import *

# have to import rpc views manually
# from exeapp.views.package_outline_rpc import *

urlpatterns = patterns('exeapp.views',
   (r'^$', 'package.package_main'),
   (r'authoring/$', 'authoring.authoring'),
   (r'authoring/handle_action/$', 'authoring.handle_action'),
   (r'authoring/link_list/$', 'authoring.link_list'),
   (r'authoring/(?P<page_name>\w*).html$', 'authoring.change_page'),
   (r'download/(?P<format>\w*)/$', 'package.export'),
)