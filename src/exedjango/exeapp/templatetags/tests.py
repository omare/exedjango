import unittest
from BeautifulSoup import BeautifulSoup

from exeapp.templatetags.idevice_extras import idevice_ul

class IdeviceTagTestCase(unittest.TestCase):
    
    class Prototype(object):
        
        def __init__(self, id, title):
            self.id = id
            self.title = title
            
    groups = {'Main' : [Prototype(1,'p1'), Prototype(2, 'p2')], 
     'Secondary' : [Prototype(3, 'p3'), Prototype(4, 'p4')]}
    group_order = ['Secondary', 'Main']
    
    def test_idevice_ul(self):
        soup = BeautifulSoup(idevice_ul(self.groups, self.group_order))
        self.assertTrue(len(soup.fetch('a')) == 4)
        self.assertTrue(len(soup.fetch('li')) == 6)
        self.assertTrue(len(soup.fetch('ul')) == 2)
        self.assertTrue('Secondary' in soup.find('li').contents[0])
        
        
    