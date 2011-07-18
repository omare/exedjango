from django.db import models
from exe.engine.idevice import Idevice

class GlossaryIdeviceManager(models.Manager):
    def create(self):
        idevice = GlossaryIdevice()
        idevice.save()
        GlossaryTerm.objects.create(title="", definition="", idevice=idevice)
    
class GlossaryIdevice(models.Model):
    
    name = "Glossary"
    title = models.CharField(max_length=100, default=name)
    author = "Technical University Munich"
    purpose = "Adds a alphabethicaly sorted glossary"
    emphasis = Idevice.SomeEmphasis
    group    = Idevice.Content
    icon = u"icon_summary.gif"
    
    objects = GlossaryIdeviceManager()
    
    class Meta:
        app_label = "exeapp"
    

class GlossaryTerm(models.Model):
    
    title = models.CharField(max_length=100, blank=True, default="",
                             help_text="Enter term you want to describe")
    defintion = models.TextField(blank=True,
                                 help_text="Enter defintion of the term")
    idevice = models.ForeignKey(GlossaryIdevice, related_name="terms")
    
    class Meta:
        app_label = "exeapp"
