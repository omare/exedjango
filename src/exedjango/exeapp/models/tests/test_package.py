from django.test import TestCase
from django.db import models
from django.contrib.auth.models import User

from exeapp.models import  package_store


from exeapp.models import Package

class UserandPackageTestCase(TestCase):
    TEST_USER = 'admin'
    TEST_EMAIL = 'admin@exe.org'
    TEST_PASSWORD = 'admin'
    PACKAGE_TITLE = 'admins package'
    
    def setUp(self):
        self.user = User.objects.create_user(self.TEST_USER,
                                    self.TEST_PASSWORD)
        Package.objects.create(title=self.PACKAGE_TITLE, user=self.user)
        self.package = Package.objects.get(id=1)
    
    def tearDown(self):
        package_store.clear()
        
    def test_get_user_from_package(self):
        self.assertEquals(self.package.user,
                           User.objects.get(username='admin'))
        
    def test_persistent_package(self):
        self.assertTrue(self.package.id in package_store)
        self.assertEquals(package_store[self.package.id].name,
                           self.PACKAGE_TITLE)
        self.package.save_persist()
        
    def test_get_persistent_package(self):
        self.package.save_persist()
        del package_store[self.package.id]
        persist_package = self.package.get_persist_package()
        self.assertEquals(persist_package.name, self.PACKAGE_TITLE)
        