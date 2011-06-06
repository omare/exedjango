# Django settings for exedjango project.

import os, sys

def _get_file_from_root(folder_name):
    '''Returns path to a file or folder in root of the project'''
    return os.path.join(os.path.dirname(__file__), folder_name).replace('\\', '/')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

if DEBUG:
    sys.dont_write_bytecode = True

import logging
logging.basicConfig(
            level = DEBUG and logging.DEBUG or logging.INFO,
            format = '%(asctime)s %(levelname)s %(message)s',
            )

ADMINS = (
    ('Dmytro Vorona', 'alendit@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': _get_file_from_root('sqlite.db'),                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = _get_file_from_root('exeapp_media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'g4c9r)uzvpig@%g5mc+6i$6o6tm-qh@^l=*8=#hw+jo_j_*fl_'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    
    #handling of 403 exception
    'exedjango.base.middleware.Http403Middleware',
)

ROOT_URLCONF = 'exedjango.urls'

TEMPLATE_DIRS = (_get_file_from_root('exeapp_templates'),
                 )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django_extensions',
    'jsonrpc',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'tinymce',
    'exeapp',
    'filebrowser',
)

STATIC_ROOT = _get_file_from_root('static')
STATIC_URL = '/static/'
STYLE_DIR = "%s/css/styles/" % STATIC_ROOT

TINYMCE_JS_URL = os.path.join(STATIC_URL, 'tiny_mce/tiny_mce.js')
TINYMCE_JS_ROOT = os.path.join(STATIC_ROOT, 'tiny_mce')

TINYMCE_COMPRESSOR = True

TINYMCE_DEFAULT_CONFIG = {   
    "content_css" : "/static/css/extra.css", 
     "strict_loading_mode" : True,
    "apply_source_formatting" : True, 
    "cleanup_on_startup" : False, 
    "entity_encoding" : "raw", 
    "gecko_spellcheck" : True, 
     #"mode" : "specific_textareas",
     #"editor_selector" : "mceEditor",
     "plugins" : "table,save,advhr,advimage,advlink,emotions,media, contextmenu,paste,directionality",
     "theme" : "advanced",
     "theme_advanced_layout_manager" : "SimpleLayout",
    "theme_advanced_toolbar_location" : "top",
     "theme_advanced_buttons1" : "newdocument,separator,bold,italic,underline,fontsizeselect,forecolor,backcolor,separator,sub,sup,separator,justifyleft,justifycenter,justifyright,justifyfull,separator,bullist,numlist,outdent,indent,separator,anchor,separator,cut,copy,paste,pastetext,pasteword,help",
     "theme_advanced_buttons2" : "image,media,exemath,advhr,fontselect,tablecontrols,separator,link,unlink,separator, undo,redo,separator,charmap,code,removeformat",
     "theme_advanced_buttons3" : "",
    "advimage_image_browser_callback" : "chooseImage_viaTinyMCE",
    "advimage_image2insert_browser_callback" : "chooseImage_viaTinyMCE",
    "media_media_browser_callback" : "chooseImage_viaTinyMCE",
    "media_media2insert_browser_callback" : "chooseImage_viaTinyMCE",
    "advlink_file_browser_callback" : "chooseImage_viaTinyMCE",
    "advlink_file2insert_browser_callback" : "chooseImage_viaTinyMCE",
    "theme_advanced_statusbar_location" : "bottom",
        "theme_advanced_resize_horizontal" : True,
        "theme_advanced_resizing" : True,
        "width" : "100%"
 }

# filebrowser settings
FILEBROWSER_PATH_FILEBROWSER_MEDIA = "%s/filebrowser/" % STATIC_ROOT
FILEBROWSER_URL_FILEBROWSER_MEDIA = "%sfilebrowser/" % STATIC_URL

FILEBROWSER_URL_TINYMCE = "%stiny_mce/" % STATIC_URL
FILEBROWSER_PATH_TINYMCE = "/tinymce/" 