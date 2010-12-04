import unittest
from BeautifulSoup import BeautifulSoup

from exeapp.templatetags.mainpage_extras import idevice_ul, nodes_ul

class MainpageExtrasTestCase(unittest.TestCase):
    
    class Prototype(object):
        '''A mock idevice'''
        def __init__(self, id, title):
            self.id = id
            self.title = title
            
    groups = {'Main' : [Prototype(1,'p1'), Prototype(2, 'p2')], 
     'Secondary' : [Prototype(3, 'p3'), Prototype(4, 'p4')]}
    group_order = ['Secondary', 'Main']
    
  
    def test_idevice_ul(self):
        soup = BeautifulSoup(idevice_ul(self.groups, self.group_order))
        self.assertEquals(len(soup.fetch('a')), 4)
        self.assertEquals(len(soup.fetch('li')), 6)
        self.assertEquals(len(soup.fetch('ul')), 2)
        self.assertTrue('Secondary' in soup.find('li').contents[0])
        
    class Node(object):
        '''A mock node'''
        def __init__(self, id, title, children, current = False):
            self.id = id
            self.title = title
            self.children = children
            self.current = current
            
        def is_current_node(self):
            return self.current
            
    root = Node(1, 'Root' ,
        [Node(2, 'Child1', [Node(3, 'Grandchild1', []), Node(4, 'Grandchild2', [])]),
        Node(5, 'Child2', [])], current=True)

    def test_nodes_ul(self):
        print nodes_ul(self.root)
        soup = BeautifulSoup(nodes_ul(self.root))
        root = soup.find(attrs={'nodeid' : '1'})
        self.assertTrue('Root' in root.contents[0])
        self.assertTrue('curNode' in root.get('class'))
        self.assertEquals(len(soup.fetch('li')), 6)
        self.assertEquals(len(soup.fetch('ul')), 3)
    