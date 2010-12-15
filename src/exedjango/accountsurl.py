from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

urlpatterns = patterns('',
                (r'^login/$', login),
                (r'^logout/$', logout),
                (r'^registration/$', "exeapp.views.registration.register"),
                (r'', 'exeapp.views.main.main'),
            )