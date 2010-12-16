from django.test import TestCase
from django.db import models
from django.contrib.auth.models import User

from exeapp.models import  package_storage


from exeapp.models import Package

class UserandPackageTestCase(TestCase):
    TEST_USER = 'admin'
    TEST_EMAIL = 'admin@exe.org'
    TEST_PASSWORD = 'admin'
    PACKAGE_TITLE = 'admins package'
    PACKAGE_ID = 1
    
    def setUp(self):
        self.user = User.objects.create_user(self.TEST_USER,
                                    self.TEST_PASSWORD)
        Package.objects.create(title=self.PACKAGE_TITLE, user=self.user)
        self.package = Package.objects.get(id=self.PACKAGE_ID)
    
    def tearDown(self):
        package_storage.clear()
        
    def test_get_user_from_package(self):
        self.assertEquals(self.package.user,
                           User.objects.get(username='admin'))
        
    def test_persistent_package(self):
        self.assertTrue(self.package.id in package_storage)
        self.assertEquals(package_storage[self.package.id].name,
                           self.PACKAGE_TITLE)
        self.package.save_data_package()
        
    def test_get_persistent_package(self):
        self.package.save_data_package()
        del package_storage[self.package.id]
        persist_package = self.package.get_data_package()
        self.assertEquals(persist_package.name, self.PACKAGE_TITLE)
        
