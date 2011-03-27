# Django settings for exedjango project.

from settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
        'default' : {
                'ENGINE' : 'django.db.backends.mysql',
                'NAME' : 'exedjangodb',
                'USER' : 'root',
                'PASSWORD' : 'ssl20qwerty',
                'HOST' : 'localhost',
                'PORT' : '',
        }
}
