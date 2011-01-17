from django.test import TestCase
from django.db import models
from django.contrib.auth.models import User


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
    
        
    def test_get_user_from_package(self):
        self.assertEquals(self.package.user,
                           User.objects.get(username='admin'))
        
    
