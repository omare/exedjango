from django.db import models
from exeapp.models.idevices.idevice import Idevice
import re
from django.conf import settings

class ActivityIdevice(Idevice):

    group = Idevice.Content
    name = "Activity"
    title = models.CharField(max_length=100, default=name) 
    author = "University of Auckland"
    purpose = """An activity can be defined as a task or set of tasks a 
learner must complete. Provide a clear statement of the task and consider
any conditions that may help or hinder the learner in the performance of 
the task."""
    icon = "icon_activity.gif"
    emphasis = Idevice.SomeEmphasis
    content = models.TextField(blank=True, default="",
                help_text="Describe the tasks the learners should complete.")
    
    
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
    def icon_url(self):
        print "#" * 10
        icon_url = "%scss/styles/%s/%s" % (settings.STATIC_URL,
                                           self.parent_node.package.style,
                                           self.icon)
        print icon_url
        return icon_url
    
    def __unicode__(self):
        return "ActivityIdevice: %s" % self.pk
    class Meta:
        app_label = "exeapp"
                                       
