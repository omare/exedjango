import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'exedjango.deployment_settings'

sys.path += ['/home/vorona/', '/home/vorona/exedjango'] 

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

