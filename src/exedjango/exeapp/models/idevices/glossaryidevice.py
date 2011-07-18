from django.db import models
from exeapp.models.idevices.idevice import Idevice

class GlossaryIdeviceManager(models.Manager):
    def create(self, *args, **kwargs):
        idevice = GlossaryIdevice(*args, **kwargs)
        idevice.save()
        GlossaryTerm.objects.create(title="", definition="", idevice=idevice)
        return idevice
    
class GlossaryIdevice(Idevice):
    
    name = "Glossary"
    title = models.CharField(max_length=100, default=name)
    author = "Technical University Munich"
    purpose = "Adds a alphabethicaly sorted glossary"
    emphasis = Idevice.SomeEmphasis
    group    = Idevice.Content
    icon = "icon_summary.gif"
    
    objects = GlossaryIdeviceManager()
    
    def add_term(self):
        GlossaryTerm.objects.create(idevice=self)
    
    class Meta:
        app_label = "exeapp"
    

class GlossaryTerm(models.Model):
    
    title = models.CharField(max_length=100, blank=True, default="",
                             help_text="Enter term you want to describe")
    definition = models.TextField(blank=True, default="",
                                 help_text="Enter defintion of the term")
    idevice = models.ForeignKey("GlossaryIdevice", related_name="terms")
    
    class Meta:
        app_label = "exeapp"
