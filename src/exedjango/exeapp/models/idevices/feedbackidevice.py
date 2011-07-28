from django.db import models
from exeapp.models.idevices.idevice import Idevice


class FeedbackIdevice(Idevice):
    name = "Feedback"
    title = "Feedback"
    author = "Dimitri Vorona"
    purpose = "Use it to put a feedback link to your documents"
    emphasis = Idevice.SOMEEMPHASIS
    icon = "icon_question.gif"
    group = Idevice.COMMUNICATION
    
    email = models.EmailField(max_length=50, blank=True, default="")
    subject = models.CharField(max_length=200, blank=True, default="")
    
    def save(self, *args, **kwargs):
        authors_email = self.parent_node.package.email
        if authors_email:
            self.email = authors_email
        self.subject = "%s - %s" % (self.parent_node.package.title,
                                  self.parent_node.title)
        super(FeedbackIdevice, self).save(*args, **kwargs)
        
    class Meta:
        app_label = "exeapp"