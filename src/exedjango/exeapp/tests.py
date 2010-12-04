"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

import os, shutil
from mock import Mock

from django.test import TestCase, Client
from django.contrib import auth
from django.utils.html import escape
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseForbidden, Http404
from jsonrpc.proxy import ServiceProxy

from exeapp.models import User, Package
from exeapp.models.persist_package_store import package_storage
from exeapp.templatetags.tests import MainpageExtrasTestCase
from exedjango.exeapp.models.data_package import DataPackage
from exedjango.exeapp.shortcuts import get_package_by_id_or_error
from exedjango.base.http import Http403


PACKAGE_COUNT = 3
PACKAGE_NAME_TEMPLATE = '%s\'s Package %s'
    
def _create_packages(user, package_count=PACKAGE_COUNT,
                      package_name_template=PACKAGE_NAME_TEMPLATE):
        for x in xrange(package_count):
            Package.objects.create(title=package_name_template % (user.username,x),
                                   user=user)

def _create_basic_database():
    '''Creates 2 users (admin, user) with 5 packages each for testing'''
    admin = User.objects.create_superuser(username='admin', email='admin@exe.org', 
                                          password='admin')
    admin.save()
    user = User.objects.create_user(username='user', email='admin@exe.org',
                                          password='user')
    user.save()
    _create_packages(admin)
    _create_packages(user)
    
def _clean_up_database_and_store():
    try:
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 'packages'))
    except:
        pass
    package_storage.clear()
    
    
class MainPageTestCase(TestCase):
    TEST_USER = 'admin'
    TEST_PASSWORD = 'admin'
    
    def _create_packages(self, user):
        for x in xrange(self.COUNT):
            Package.objects.create(title=self.PACKAGE_NAME_TEMPLATE % (user.username,x),
                                   user=user)
    
    def setUp(self):
        
        _create_basic_database()
        self.c = Client()
        # login
        self.c.login(username=self.TEST_USER, password=self.TEST_PASSWORD)
        self.s = ServiceProxy('http://locahost:8000/json/')
    
    def tearDown(self):
        _clean_up_database_and_store()
        
    def test_basic_elements(self):
        response = self.c.get('/exeapp/')
        self.assertContains(response, "Main Page")
        self.assertContains(response, "Package")
        
    def _test_create_package(self):
        PACKAGE_NAME = '%s Package post' % self.TEST_USER
        response = self.s.app.register(PACKAGE_NAME)
        p = Package.objects.get(title=PACKAGE_NAME)
        self.assertTrue(p.user.username == self.TEST_USER)
        
        
    def test_require_login(self):
        self.c.logout()
        response = self.c.get('/exeapp/main')
        self.assertFalse('Main Page' in response.content)
        
class PackagesPageTestCase(TestCase):
    
    PAGE_URL = '/exeapp/package/%s/'
    PACKAGE_ID = 1
    
    def setUp(self):
        self.c = Client()
        _create_basic_database()
        self.c.login(username='admin', password='admin')
        
    def tearDown(self):
        _clean_up_database_and_store()
        
    
    def test_basic_structure(self):
        response = self.c.get(self.PAGE_URL % self.PACKAGE_ID)
        package_title = Package.objects.get(id=self.PACKAGE_ID).title
        self.assertContains(response, escape(package_title))
        
    def test_outline_pane(self):
        response = self.c.get(self.PAGE_URL % self.PACKAGE_ID)
        self.assertContains(response, "outlinePane")
        
    def test_idevice_pane(self):
        response = self.c.get(self.PAGE_URL % self.PACKAGE_ID)
        self.assertContains(response, "outlinePane")
        self.assertContains(response, "Free Text")
    
    def test_authoring(self):
        response = self.c.get(self.PAGE_URL % self.PACKAGE_ID + "authoring/")
        self.assertContains(response, "Authoring")
        self.assertContains(response, self.PACKAGE_ID)
        
    def test_properties(self):
        response = self.c.get(self.PAGE_URL % self.PACKAGE_ID + "properties/")
        self.assertContains(response, "Properties")
        self.assertContains(response, self.PACKAGE_ID)
        
        
    def test_404_on_wrong_package(self):
        ## this id shouldn't be created
        WRONG_PACKAGE_ID = PACKAGE_COUNT * 2 + 1
        response = self.c.get(self.PAGE_URL % WRONG_PACKAGE_ID)
        self.assertTrue(isinstance(response, HttpResponseNotFound))
        
    
    def test_403_on_wrong_user(self):
        USERS_PACKAGE_ID = PACKAGE_COUNT + 1
        response = self.c.get(self.PAGE_URL % USERS_PACKAGE_ID)
        self.assertTrue(isinstance(response, HttpResponseForbidden))
        
class ShortcutTestCase(TestCase):
    PACKAGE_ID = 1
    NON_EXISTENT_PACKAGE_ID = 9001 # over 9000
    PACKAGE_TITLE = "test"
    TEST_USER = 'admin'
    WRONG_USER = 'foo'
    TEST_PASSWORD = 'admin'
    TEST_ARG = 'arg'
    
    def test_get_package_or_error(self):
        '''Tests exeapp.shortcuts.get_package_by_id_or_error convinience decorator'''
        # mock request
        request = Mock()
        request.user = Mock()
        request.user.username = self.TEST_USER
        # mock view, doesn't return a response object
        @get_package_by_id_or_error
        def mock_view(request, package, arg):
            return package, arg
        user = User.objects.create_user(username=self.TEST_USER,
                                        email = '',
                                        password=self.TEST_PASSWORD)
        package = Package.objects.create(self.PACKAGE_TITLE, user)
        user.save()
        package.save()
        
        package, arg = mock_view(request, self.PACKAGE_ID, self.TEST_ARG)
        self.assertEquals(package.title, self.PACKAGE_TITLE)
        self.assertEquals(arg, self.TEST_ARG)
        self.assertRaises(Http404, mock_view, request, 
                          self.NON_EXISTENT_PACKAGE_ID)
        request.user.username = self.WRONG_USER
        self.assertRaises(Http403, mock_view, request,
                          self.PACKAGE_ID)