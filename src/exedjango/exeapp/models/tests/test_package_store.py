from mock import Mock

from django.test import TestCase

from exeapp.models.data_package_store\
                     import PackageStore, AlreadyRegistredError



class PackageStoreTestCase(TestCase):
    
    PACKAGE_ID = "1"
    
    
    def setUp(self):
        self.package_store = PackageStore()
        super(PackageStoreTestCase, self).setUp()
        self.package = Mock()
        self.package_store[self.PACKAGE_ID] = self.package
        
    def tearDown(self):
        self.package_store.clear()
        
        
    def test_add(self):
        self.assertEquals(self.package, self.package_store[self.PACKAGE_ID])
        
    def test_remove(self):
        del self.package_store[self.PACKAGE_ID]
        self.assertRaises(KeyError, self.package_store.__getitem__, self.PACKAGE_ID)
        
    def test_adding_same_id(self):
        package2 = Mock()
        self.assertRaises(AlreadyRegistredError, self.package_store.__setitem__,
                          self.PACKAGE_ID, package2)