"""
This file contains the tests for important views in exedjango.
Notice, that your tests should always clear package_storage shoudl be cleared,
to prevent conflicts with package creation in another tests. You can use 
_clean_up_database_and_store for it.
"""

import os, sys, shutil
from mock import Mock

from django.test import TestCase, Client
from django.contrib import auth
from django.utils.html import escape
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseForbidden, Http404
from jsonrpc.proxy import ServiceProxy

from exeapp.models import User, DataPackage, Package
from exeapp.models.data_package_store import package_storage
from exeapp.templatetags.tests import MainpageExtrasTestCase
from exeapp.views.export.websiteexport import WebsiteExport, _generate_pages
from exedjango.exeapp.shortcuts import get_package_by_id_or_error
from exedjango.base.http import Http403
from exeapp.views.export.websitepage import WebsitePage




PACKAGE_COUNT = 3
PACKAGE_NAME_TEMPLATE = '%s\'s DataPackage %s'
    
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
    if sys.platform[:3] != 'win':
        # Doesn't work on windows because of access permission. MEDIA_ROOT will
        # be removed on test suit start
        try:
            shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 'packages'))
        except remove_exception:
            print "%s couldn't be removed" % settings.MEDIA_ROOT
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
        self.assertContains(response, "DataPackage")
        
    def _test_create_package(self):
        PACKAGE_NAME = '%s DataPackage post' % self.TEST_USER
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
        '''Tests exeapp.shortcuts.get_package_by_id_or_error convinience
decorator'''
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
        
class AuthoringTestCase(TestCase):
    '''Tests the authoring view. The it ill be brought together with package
view, this tests should be also merged'''

    TEST_PACKAGE_ID = 1
    TEST_NODE_ID = 0
    TEST_NODE_TITLE = "Home"
    
    VIEW_URL = "/exeapp/package/%s/authoring/" % TEST_PACKAGE_ID
    
    
    def setUp(self):
        self.c = Client()
        _create_basic_database()
        self.c.login(username='admin', password='admin')

    def tearDown(self):
        _clean_up_database_and_store()
        
    def test_basic_elements(self): 
        '''Basic tests aimed to determine if this view works at all'''
        response = self.c.get(self.VIEW_URL)
        self.assertContains(response, 'Package %s' % self.TEST_PACKAGE_ID)
        self.assertContains(response, 'Rendering node %s' % self.TEST_NODE_ID)
        self.assertContains(response, self.TEST_NODE_TITLE)
        
class ExportTestCase(TestCase):
    
    TEST_PACKAGE_ID = 1
    
    def setUp(self):
        _create_basic_database()
        self.data = Package.objects.get(id=self.TEST_PACKAGE_ID).get_data_package()
        for x in range(3):
            self.data.add_child_node()
        
    def tearDown(self):
        _clean_up_database_and_store()
        
    def test_basic_export(self):
        '''Exports a package'''
        
        exporter = WebsiteExport(self.data, settings.MEDIA_ROOT + "/111.zip")
        exporter.exportZip()
        
    def test_pages_generation(self):
        '''Tests generation of the page nested list'''
        class MockNode(object):
            def __init__(self, title):
                self.title = title
                self.children = []
                self.is_root = False
                
        nodes = [MockNode("Node%s" % x) for x in range(4)]
        nodes[0].is_root = True
        nodes[0].children = [nodes[1], nodes[2]]
        nodes[2].children = [nodes[3]]
        pages = _generate_pages(nodes[0], 1)
        pages.insert(0, None)
        pages.append(None)
        for i in range(1, len(pages) - 1):
            page = pages[i]
            if page != 'in' and page != 'out':
                prev = i - 1
                while pages[prev] == 'in' or pages[prev] == 'out':
                    prev -= 1
                next = i + 1
                while pages[next] == 'in' or pages[next] == 'out':
                    next += 1
                
                self.assertEquals(page.prev_page, pages[prev])
                self.assertEquals(page.next_page, pages[next])