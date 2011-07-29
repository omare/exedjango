from django.db import models

from exeapp.models.idevices.genericidevice import GenericIdevice
from exeapp.models.idevices.idevice import Idevice
from exeapp.models.idevices import fields


class ReadingActivityIdevice(GenericIdevice):
    group = Idevice.CONTENT
    name = "Reading Activity"
    title = models.CharField(max_length=100, default=name)
    author = "University of Auckland"
    purpose = """<p>The Reading Activity will primarily 
be used to check a learner's comprehension of a given text. This can be done 
by asking the learner to reflect on the reading and respond to questions about 
the reading, or by having them complete some other possibly more physical task 
based on the reading.</p>"""
    icon = "icon_reading.gif"
    emphasis = Idevice.SOMEEMPHASIS
    to_read = fields.RichTextField(blank=True, default="",
                               help_text="""Enter the details of the reading including reference details. The 
referencing style used will depend on the preference of your faculty or 
department.""")
    activity = fields.RichTextField(blank=True, default="",
                                help_text="""Describe the tasks related to the reading learners should undertake. 
This helps demonstrate relevance for learners.""")
    feedback = fields.FeedbackField(blank=True, default="",
                                help_text="""Use feedback to provide a summary of the points covered in the reading, 
or as a starting point for further analysis of the reading by posing a question 
or providing a statement to begin a debate.""")
    
    class Meta:
        app_label = "exeapp"
    