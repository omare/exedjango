from django.db import models
from exeapp.models.idevices.idevice import Idevice
from exeapp.models.idevices import fields


class ExternalURLIdevice(Idevice):
    name = "External Web Site"
    title = name
    author = "University of Auckland"
    purpose = """The external website iDevice loads an external website 
into an inline frame in your eXe content rather then opening it in a popup box. 
This means learners are not having to juggle windows. 
This iDevice should only be used if your content 
will be viewed by learners online."""
    emphasis = Idevice.NOEMPHASIS
    group = Idevice.MEDIA
    url = models.CharField(max_length=200, blank=True, default="",
                        help_text="""Enter the URL you wish to display
and select the size of the area to display it in.""")
    height = models.PositiveIntegerField(default=300)
    
    class Meta:
        app_label = "exeapp"