"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

import os, shutil

from django.test import TestCase, Client
from django.contrib import auth
from django.utils.html import escape
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseForbidden

from exeapp.models import User, Package
from exeapp.models.persist_package_store import package_storage
from exeapp.templatetags.tests import IdeviceTagTestCase
from exeapp.views.package import _get_parameter_dict
from BeautifulSoup import BeautifulSoup


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
    
def _converted_soap(buffer):
    '''Conviniece funtion for creation of BeautifulSoap objects with unescaped
characters'''
    return BeautifulSoup(buffer, convertEntities=BeautifulSoup.HTML_ENTITIES)
    
    
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
    
    def tearDown(self):
        _clean_up_database_and_store()
        
    def test_basic_elements(self):
        response = self.c.get('/exeapp/main/')
        self.assertContains(response, "Main Page")
        self.assertContains(response, "Package", PACKAGE_COUNT + 3)
        
    def test_create_form(self):
        POST_PACKAGE_NAME = '%s Package post' % self.TEST_USER
        response = self.c.post('/exeapp/createpackage/',
                     data={'package_title' : POST_PACKAGE_NAME})
        p = Package.objects.get(title=POST_PACKAGE_NAME)
        self.assertTrue(p.user.username == self.TEST_USER)
        
        
    def test_require_login(self):
        self.c.logout()
        response = self.c.get('/exeapp/main')
        self.assertFalse('Main Page' in response.content)
        
class PackagesPageTestCase(TestCase):
    
    PAGE_URL = '/exeapp/package/%s/'
    
    def setUp(self):
        self.c = Client()
        _create_basic_database()
        self.c.login(username='admin', password='admin')
        
    def tearDown(self):
        _clean_up_database_and_store()
        
    
    def test_basic_structure(self):
        PACKAGE_ID = 1
        response = self.c.get(self.PAGE_URL % PACKAGE_ID)
        soup = _converted_soap(response.content)
        package_title = Package.objects.get(id=PACKAGE_ID).title
        title = soup.find('title')
        self.assertTrue(title is not None)
        self.assertEquals(title.contents[0], 'Package Page: %s' % package_title)
        self.assertTrue(len(soup.find(attrs={'id' : 'wrap'})) > 0)
        
    def test_outline_pane(self):
        PACKAGE_ID = 1
        response = self.c.get(self.PAGE_URL % PACKAGE_ID)
        self.assertContains(response, "outlinePane")
        
    def test_idevice_pane(self):
        PACKAGE_ID = 1
        response = self.c.get(self.PAGE_URL % PACKAGE_ID)
        self.assertContains(response, "outlinePane")
        self.assertContains(response, "Free Text")
        
    def test_get_parameters_list(self):
        post_dict = {'name' : 'add', 'params[title]' : 'test_node'
                     , 'params[place]' : '10'}
        expected_dict = {'title' : 'test_node', 'place' : '10'}
        
        self.assertEquals(_get_parameter_dict(post_dict), expected_dict)
        
    def test_404_on_wrong_package(self):
        ## this id shouldn't be created
        WRONG_PACKAGE_ID = PACKAGE_COUNT * 2 + 1
        response = self.c.get(self.PAGE_URL % WRONG_PACKAGE_ID)
        self.assertTrue(isinstance(response, HttpResponseNotFound))
        
    
    def test_403_on_wrong_user(self):
        USERS_PACKAGE_ID = PACKAGE_COUNT + 1
        response = self.c.get(self.PAGE_URL % USERS_PACKAGE_ID)
        self.assertTrue(isinstance(response, HttpResponseForbidden))
