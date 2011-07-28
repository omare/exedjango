from exeapp.models.idevices.genericidevice import GenericIdevice
from exeapp.models.idevices.idevice import Idevice
from django.db import models
from django.template.defaultfilters import unordered_list
from exeapp.models.idevices import fields
        
class TOCIdevice(GenericIdevice):
    name = "Table Of Content"
    title = name
    
            
    emphasis = Idevice.SOMEEMPHASIS
    group = Idevice.CONTENT
    content = fields.RichTextField(blank=True, default="")
    author = "TU Munich"
    icon = u"icon_inter.gif"
    
    def save(self, *args, **kwargs):
        self.content = self.populate_toc()
        super(TOCIdevice, self).save(*args, **kwargs)
        
    def populate_toc(self):
        package = self.parent_node.package
        toc_list = [self._generate_item(package.root)]
        if package.root.children.exists():
            toc_list.append(self._generate_toc_tree(package.root))
        return '<ul class="toc">%s</ul>' % unordered_list(toc_list)
        
    def _generate_toc_tree(self, node):
        list = []
        for child in node.children.all():
            list.append(self._generate_item(child))
            if child.children.exists():
                list.append(self._generate_toc_tree(child))
                
        return list
    
    def _generate_item(self, node):
        return '<a href="%s.html">%s</a>' %\
                    (node.unique_name(), node.title)
    class Meta:
        app_label = "exeapp"