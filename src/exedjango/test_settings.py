# Django settings for exedjango project.

import os, sys, shutil
from exedjango.settings import *
from exedjango.settings import _get_file_from_root

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    #'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    
    #handling of 403 exception
    'exedjango.base.middleware.Http403Middleware',
)

##
sys.dont_write_bytecode = True

DEBUG = True
TEMPLATE_DEBUG = DEBUG
TEST = True

MEDIA_ROOT = _get_file_from_root("exeapp_media_testing")
