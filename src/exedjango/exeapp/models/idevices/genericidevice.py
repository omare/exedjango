import re
from exeapp.models.idevices.idevice import Idevice

class GenericIdevice(Idevice):
    
    def _resources(self):
        user = self.parent_node.package.user
        reg_exp = r'src=".*?%s(.*?)"' % user.get_profile().media_url
        resource_list = set()
        for medium in re.findall(reg_exp, self.content):
            resource_list.add(medium)
        return resource_list
    
    @property
    def link_list(self):
        parent = self.parent_node
        return [("%s::%s" % (parent.title, anchor), "%s.html#%s" %\
                                              (parent.unique_name(), anchor)) \
                               for anchor in re.findall('<a.*?name=[\"\'](.*?)[\"\']>',
                                                         self.content)]
        
    class Meta:
        app_label = "exeapp"
        proxy = True
        
