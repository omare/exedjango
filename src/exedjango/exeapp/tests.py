"""
This file contains the tests for important views in exedjango.
Notice, that your tests should always clear package_storage shoudl be cleared,
to prevent conflicts with package creation in another tests. You can use 
_clean_up_database_and_store for it.
"""

import os, sys, shutil
import mock
from mock import Mock
import json
import uuid

from django.test import TestCase, Client
from django.test.client import FakePayload
from django.contrib import auth
from django.utils.html import escape
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseForbidden, Http404, QueryDict
from jsonrpc.proxy import TestingServiceProxy
from jsonrpc.types import *

from exeapp import models
from exeapp.models import User, Package
from exeapp.templatetags.tests import MainpageExtrasTestCase
from exeapp.views.export.websiteexport import WebsiteExport, _generate_pages
from exeapp import shortcuts
from exedjango.exeapp.shortcuts import get_package_by_id_or_error
from exedjango.base.http import Http403
from exeapp.views.export.websitepage import WebsitePage
from django.core.urlresolvers import reverse
from exeapp.views import authoring



PACKAGE_COUNT = 3
PACKAGE_NAME_TEMPLATE = '%s\'s Package %s'
TEST_USER = "admin"
TEST_PASSWORD = "password"
    
def _create_packages(user, package_count=PACKAGE_COUNT,
                      package_name_template=PACKAGE_NAME_TEMPLATE):
        for x in xrange(package_count):
            Package.objects.create(title=package_name_template % (user.username,x),
                                   user=user)

def _create_basic_database():
    '''Creates 2 users (admin, user) with 5 packages each for testing'''
    admin = User.objects.create_superuser(username=TEST_USER, email='admin@exe.org', 
                                          password=TEST_PASSWORD)
    admin.save()
    user = User.objects.create_user(username='user', email='admin@exe.org',
                                          password='user')
    user.save()
    _create_packages(admin)
    _create_packages(user)
    
    
    
class MainPageTestCase(TestCase):
    
    def _create_packages(self, user):
        for x in xrange(self.COUNT):
            Package.objects.create(title=self.PACKAGE_NAME_TEMPLATE % (user.username,x),
                                   user=user)
    
    def setUp(self):
        
        _create_basic_database()
        self.c = Client()
        # login
        self.c.login(username=TEST_USER, password=TEST_PASSWORD)
    
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
    NODE_ID = 1
    
    def setUp(self):
        self.c = Client()
        _create_basic_database()
        self.c.login(username=TEST_USER, password=TEST_PASSWORD)
        self.s = TestingServiceProxy(self.c,
                                reverse("jsonrpc_mountpoint"),
                                version="2.0")
        
    def test_basic_structure(self):
        response = self.c.get(self.PAGE_URL % self.PACKAGE_ID)
        package_title = Package.objects.get(id=self.PACKAGE_ID).title
        self.assertContains(response, escape(package_title))
        
    def test_outline_pane(self):
        response = self.c.get(self.PAGE_URL % self.PACKAGE_ID)
        self.assertContains(response, "outlinePane")
        self.assertContains(response, 'current_node="%s"' % self.NODE_ID)
    
    
    @mock.patch.object(Package.objects, 'get')
    def test_rpc_calls(self, mock_get):
        NODE_ID = 42
        NODE_TITLE = "Node"
        # mock node
        new_node = Mock()
        new_node.id = NODE_ID
        new_node.title = NODE_TITLE
        
        # mock package
        package = Mock()
        package.add_child_node.return_value = new_node
        package.user.username = TEST_USER
        
        #mock get query
        mock_get.return_value = package
        
        
        
        r = self.s.package.add_child_node(#username=TEST_USER,
                                     #       password=TEST_PASSWORD,
                                            package_id=1)
        result = r['result'] 
        self.assertEquals(result['id'], NODE_ID)
        self.assertEquals(result['title'], NODE_TITLE)
        self.assertTrue(package.add_child_node.called)
        
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
    
    
    @mock.patch.object(Package.objects, 'get')
    def test_get_package_or_error(self, mock_get):
        '''Tests exeapp.shortcuts.get_package_by_id_or_error convinience
decorator'''
        # mock request
        request = Mock()
        request.user.username = self.TEST_USER
        
        # mock package
        package = Mock()
        package.user.username = self.WRONG_USER
        
        #mock getter
        mock_get.return_value = package

        @get_package_by_id_or_error
        def mock_view(request, package):
            return package
                
        #package, arg = mock_view(request, self.PACKAGE_ID)
        #self.assertEquals(package.title, self.PACKAGE_TITLE)
        #self.assertEquals(arg, self.TEST_ARG)
        #self.assertRaises(Http404, mock_view, request, 
        #                  self.NON_EXISTENT_PACKAGE_ID)
        #request.user.username = self.WRONG_USER
        self.assertRaises(Http403, mock_view, request,
                          self.PACKAGE_ID)
        mock_get.assert_called_with(id=self.PACKAGE_ID)
        
        
class AuthoringTestCase(TestCase):
    '''Tests the authoring view. The it ill be brought together with package
view, this tests should be also merged'''

    TEST_PACKAGE_ID = 1
    TEST_NODE_ID = 1
    TEST_NODE_TITLE = "Home"
    IDEVICE_TYPE = "FreeTextIdevice"

    
    VIEW_URL = "/exeapp/package/%s/authoring/" % TEST_PACKAGE_ID
    
    
    def setUp(self):
        self.c = Client()
        _create_basic_database()
        self.c.login(username=TEST_USER, password=TEST_PASSWORD)
        self.data_package = Package.objects.get(pk=self.TEST_PACKAGE_ID)
        self.root = self.data_package.root

    def test_basic_elements(self): 
        '''Basic tests aimed to determine if this view works at all'''
        response = self.c.get(self.VIEW_URL)
        self.assertContains(response, 'Package %s' % self.TEST_PACKAGE_ID)
        self.assertContains(response, 'Rendering node %s' % self.TEST_NODE_ID)
        self.assertContains(response, self.TEST_NODE_TITLE)
        
    def test_idevice(self):
        '''Tests if idevice is rendered properly'''
        IDEVICE_ID = 1
        
        
        self.root.add_idevice(self.IDEVICE_TYPE)
        response = self.c.get(self.VIEW_URL)
        self.assertContains(response, 'idevice_id="%s"' % IDEVICE_ID)
        
        
    def test_idevice_move_up(self):
        FIRST_IDEVICE_ID = 1
        SECOND_IDEVICE_ID = 2
        self.root.add_idevice(self.IDEVICE_TYPE)
        self.root.add_idevice(self.IDEVICE_TYPE)
        self.data_package.handle_action(SECOND_IDEVICE_ID, "move_up", QueryDict(""))
        content = self.c.get(self.VIEW_URL).content
        self.assertTrue(content.index('idevice_id="%s"' % FIRST_IDEVICE_ID) \
                        > content.index('idevice_id="%s"' % SECOND_IDEVICE_ID))
    
    @mock.patch.object(shortcuts, 'render_idevice')
    @mock.patch.object(Package.objects, 'get')    
    def test_submit_idevice_action(self, mock_get, mock_render):
        '''Test if a POST request is delegated to package'''
        IDEVICE_ID = "1"
        IDEVICE_ACTION = "save"
        mock_get.return_value.user.username = TEST_USER
        action_args = {"test" : "a", "test2" : "1",
                       'idevice_id' : IDEVICE_ID,
                       'idevice_action' : IDEVICE_ACTION}
        
        def mock_render_idevice(idevice):
            return idevice.content
        mock_render.side_effect = mock_render_idevice
        
        response = self.c.post('%shandle_action/' % self.VIEW_URL,
                               data=action_args)
        self.assertEquals(response.status_code, 200)
        test_args = QueryDict("").copy()
        test_args.update(action_args)
        mock_get.return_value.handle_action.assert_called_with(
                                            unicode(IDEVICE_ID),
                                            "save",
                                            test_args)
   
    @mock.patch.object(shortcuts, 'render_idevice')
    @mock.patch.object(Package.objects, 'get')
    def test_render_idevice_partial(self, mock_get, mock_render):
        '''Test rendering of a single idevice if idevice_id is given'''
        IDEVICE_ID = 1
        IDEVICE_CONTENT = "Test idevice"
        # patch render_idevice
        def mock_render_idevice(idevice):
            return idevice.content
        mock_render.side_effect = mock_render_idevice
        
        # mock user
        package = mock_get.return_value
        package.user.username = TEST_USER
        # mock package return function
        package.get_idevice_for_partial.return_value.content\
                         = IDEVICE_CONTENT
        
        response = self.c.get(self.VIEW_URL, data={"idevice_id" : IDEVICE_ID})
        self.assertEquals(response.status_code, 200)
        self.assertTrue(package.get_idevice_for_partial.called)
        self.assertTrue(IDEVICE_CONTENT in response.content)
        
class ExportTestCase(TestCase):
    
    TEST_PACKAGE_ID = 1
    
    def setUp(self):
        _create_basic_database()
        self.data = Package.objects.get(id=self.TEST_PACKAGE_ID)
        for x in range(3):
            self.data.add_child_node()
        
        
    def test_basic_export(self):
        '''Exports a package'''
        
        exporter = WebsiteExport(self.data, settings.MEDIA_ROOT + "/111.zip")
        exporter.exportZip()
        
    def test_pages_generation(self):
        '''Tests generation of the page nested list'''
        class MockNode(object):
            def __init__(self, title):
                self.title = title
                self.children = MockQuerySet([])
                self.is_root = False
                
        class MockQuerySet(object):
            def __init__(self, values):
                self.values = values
            
            def all(self):
                return self.values
            
            def exists(self):
                return bool(self.values)
                
        nodes = [MockNode("Node%s" % x) for x in range(4)]
        nodes[0].is_root = True
        nodes[0].children = MockQuerySet([nodes[1], nodes[2]])
        nodes[2].children = MockQuerySet([nodes[3]])
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
                
    def test_websitepage(self):
        IDEVICE_TYPE = "FreeTextIdevice"
        IDEVICE_ID = 1
        
        self.assertEquals(self.data.root, self.data.current_node)
        self.data.add_idevice(IDEVICE_TYPE)
        websitepage = WebsitePage(self.data.root, 0)
        self.assertTrue('class="%s" id="id1"' % IDEVICE_TYPE \
                        in websitepage.render([self.data.root]))
        
class MiddleWareTestCase(TestCase):
    
    
    def test_403_middleware(self):
        '''Test the HTTP403 handlingmiddle ware.
Should set status code to 403'''
        from django.conf.urls.defaults import patterns
        from exeapp.urls import urlpatterns
        from exeapp import views
        
        # patch new test view which raises Http403
        views.test = Mock()
        views.test.side_effect = Http403
        urlpatterns += patterns('',
                            ("test/$", 'exeapp.views.test'))
        c = Client()
        response = c.get('/exeapp/test/')
        self.assertEquals(response.status_code, 403)