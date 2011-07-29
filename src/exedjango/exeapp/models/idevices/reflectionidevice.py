from exeapp.models.idevices.genericidevice import GenericIdevice
from django.db import models
from exeapp.models.idevices import fields
from exeapp.models.idevices.idevice import Idevice


class ReflectionIdevice(GenericIdevice):
    name = "Reflection"
    title = models.CharField(max_length=100, default=name)
    author = "University of Auckland"
    purpose = """Reflection is a teaching method often used to 
connect theory to practice. Reflection tasks often provide learners with an 
opportunity to observe and reflect on their observations before presenting 
these as a piece of academic work. Journals, diaries, profiles and portfolios 
are useful tools for collecting observation data. Rubrics and guides can be 
effective feedback tools."""
    emphasis         = Idevice.SOMEEMPHASIS
    group            = Idevice.CONTENT
    activity = fields.RichTextField(blank=True, default="",
                                      help_text="""Enter a question for learners 
to reflect upon.""")
    answer = fields.FeedbackField(blank=True, default="",
                                   help_text="""Describe how learners will assess how 
they have done in the exercise. (Rubrics are useful devices for providing 
reflective feedback.)""")
    
    class Meta:
        app_label = "exeapp"
