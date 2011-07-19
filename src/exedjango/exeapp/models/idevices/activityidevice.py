from django.db import models
from exeapp.models.idevices.idevice import Idevice
import re
from django.conf import settings
from exeapp.models.idevices.genericidevice import GenericIdevice

class ActivityIdevice(GenericIdevice):

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
    

    
    class Meta:
        app_label = "exeapp"
                                       
