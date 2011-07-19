import re
from exeapp.models.idevices.idevice import Idevice
from django.db.models.fields import TextField

class GenericIdevice(Idevice):

    def _get_text_fields(self):
        return (getattr(self, field.attname) for field in self._meta._fields() if 
                isinstance(field, TextField))
        
    def _resources(self):
        user = self.parent_node.package.user
        reg_exp = r'src=".*?%s(.*?)"' % user.get_profile().media_url
        resource_list = set()
        for field in self._get_text_fields():
            for medium in re.findall(reg_exp, field):
                resource_list.add(medium)
        return resource_list
    
    @property
    def link_list(self):
        parent = self.parent_node
        link_list = []
        for field in self._get_text_fields():
            link_list += (("%s::%s" % (parent.title, anchor), "%s.html#%s" %\
                                          (parent.unique_name(), anchor)) \
                   for anchor in re.findall('<a.*?name=[\"\'](.*?)[\"\']>',
                                                         field))
            
        return link_list
        
    def __unicode__(self):
        return "%s: %s" % (self.__class__.__name__, self.pk)
        
    class Meta:
        app_label = "exeapp"
        proxy = True
        
