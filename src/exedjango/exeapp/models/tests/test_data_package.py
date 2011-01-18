from django.test import TestCase
from django.db import models
from django.contrib.auth.models import User


from exeapp.models import Package

class DataPackageTestCase(TestCase):
    TEST_USER = 'admin'
    TEST_EMAIL = 'admin@exe.org'
    TEST_PASSWORD = 'admin'
    PACKAGE_TITLE = 'admins package'
    PACKAGE_ID = 1
    
    def setUp(self):
        self.user = User.objects.create_user(self.TEST_USER,
                                    self.TEST_PASSWORD)
        Package.objects.create(title=self.PACKAGE_TITLE, user=self.user)
        self.data_package = Package.objects.\
            get(id=self.PACKAGE_ID).get_data_package()
        self.root = self.data_package.root
        for x in range(3):
            child = self.root.create_child()
            child.title = "node%s" % x
            child.save()

    def test_get_root_from_package(self):
        root = self.data_package.root
        self.assertEquals(root.title, "Home")
        
    def test_move_up(self):
        self.assertFalse(self.root.children.all()[0].up())
        
        self.assertTrue(self.root.children.all()[2].up())
        self.assertEquals(self.root.children.all()[1].title, "node2")
        self.assertEquals(self.root.children.all()[2].title, "node1")
        
    def test_move_down(self):
        self.assertFalse(self.root.children.all()[2].down())
        self.assertTrue(self.root.children.all()[0].down())
        self.assertEquals(self.root.children.all()[0].title, "node1")
        self.assertEquals(self.root.children.all()[1].title, "node0")
        
    def test_move_next_to_last_down(self):
        self.assertTrue(self.root.children.all()[1].down())
        self.assertEquals(self.root.children.all()[1].title, "node2")
        self.assertEquals(self.root.children.all()[2].title, "node1")

        
    def test_promote(self):
        child = self.root.children.all()[1].create_child()
        child.title = "node4"
        child.save()
        self.assertTrue(child.promote())
        self.assertEquals(self.root.children.all()[2].title, child.title)
        self.assertFalse(child.promote())
        
    def test_promote_last(self):
        child = self.root.children.all()[2].create_child()
        child.title = "node4"
        child.save()
        self.assertTrue(child.promote())
        self.assertEquals(self.root.children.all()[3].title, child.title)
        self.assertFalse(child.promote())
        
    def test_demote(self):
        first_child = self.root.children.all()[0]
        self.assertFalse(first_child.demote())
        child = self.root.children.all()[1]
        self.assertTrue(child.demote())
        self.assertEquals(first_child.children.all()[0].title, child.title)
    
    def test_level_counting(self):
        child = self.root.children.all()[0].create_child()
        self.assertEquals(3, child.level)
        
    def test_change_node(self):
        self.data_package.set_current_node_by_id(2)
        self.assertTrue(self.root.children.all()[0].is_current_node)
