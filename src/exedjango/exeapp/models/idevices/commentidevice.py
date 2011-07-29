from django.db import models
from exeapp.models.idevices import fields
from exeapp.models.idevices.idevice import Idevice
from exeapp.models.idevices.genericidevice import GenericIdevice


class CommentIdevice(GenericIdevice):
    name = "Remark"
    title = models.CharField(max_length=100, default=name)
    author = "TU Munich"
    purpose =  "Leave a commentary for others who work on this package."
    emphasis = Idevice.SOMEEMPHASIS
    icon = "icon_summary.gif"
    group = Idevice.DIDACTICS
    content = fields.RichTextField(blank=True, default="",
                        help_text="""Use this field to leave a
comment for people who works on this package with you. 
This iDevice won't be exported""")

    class Meta:
        app_label = "exeapp"