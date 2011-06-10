import unittest
from mock import Mock
from BeautifulSoup import BeautifulSoup

from exeapp.templatetags.mainpage_extras import idevice_ul
from exeapp.templatetags.authoring_extras import *
from django import template
from django.template.loader import render_to_string

class MainpageExtrasTestCase(unittest.TestCase):
    
    class Prototype(object):
        '''A mock idevice'''
        def __init__(self, id, title):
            self.id = id
            self.__name__ = title.replace(" ", "")
            self.title = title
            
    groups = {'Main' : [Prototype(1,'p1'), Prototype(2, 'p2')], 
     'Secondary' : [Prototype(3, 'p3'), Prototype(4, 'p4')]}
    group_order = ['Secondary', 'Main']
    
  
    def test_idevice_ul(self):
        soup = BeautifulSoup(idevice_ul(self.groups, self.group_order))
        self.assertEquals(len(soup.fetch('a')), 6)
        self.assertEquals(len(soup.fetch('li')), 6)
        self.assertEquals(len(soup.fetch('ul')), 2)
        self.assertTrue('Secondary' in soup.find('li').contents[0])
        
    class Node(object):
        '''A mock node'''
        def __init__(self, id, title, children, current = False):
            self.id = id
            self.title = title
            self.children = Mock()
            self.children.all = Mock(return_value=children)
            self.current = current
            
        def is_current_node(self):
            return self.current
        
    class Package(object):
        '''Mock for the package'''
        def __init__(self, root):
            self.root = root
            
    root = Node(1, 'Root' ,
        [Node(2, 'Child1', [Node(3, 'Grandchild1', []), Node(4, 'Grandchild2', [])]),
        Node(5, 'Child2', [])], current=True)
    
    package = Package(root)

    def test_render_outline (self):
        c = template.Context({"package" : self.package})
        
        t = template.Template('''
        {% load mainpage_extras %}
        {% render_outline package %}
        ''')
        output = t.render(c)
        
        soup = BeautifulSoup(output)
        root = soup.find(attrs={'nodeid' : '1'})
        self.assertTrue('Root' in root.contents[0])
        self.assertEquals(len(soup.fetch('li')), 5)
        self.assertEquals(len(soup.fetch('a')), 5)
        self.assertEquals(len(soup.fetch('ul')), 3)
