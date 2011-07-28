from exeapp.models.idevices.genericidevice import GenericIdevice
from django.db import models
from exeapp.models.idevices.idevice import Idevice
from exeapp.models.idevices import fields


class ObjectivesIdevice(GenericIdevice):
    
    name = "Objectives"
    title = fields.TitleField(max_length=100, default=name)
    author = "University of Auckland"
    purpose = """Objectives describe the expected outcomes of the learning and should
define what the learners will be able to do when they have completed the
learning tasks."""
    emphasis = Idevice.SOMEEMPHASIS
    content = fields.RichTextField(blank=True, default="", 
                  help_text="Type the learning objectives for this resource.")
    group = Idevice.DIDACTICS
    
    class Meta:
        app_label = "exeapp"
