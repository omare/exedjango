from django.db import models
from exeapp.views.blocks.widgets import *

class RichTextField(models.TextField):
    
    def formfield(self, **kwargs):
        kwargs["widget"] = FreeTextWidget
        return super(RichTextField, self).formfield(**kwargs)
    
class FeedbackField(models.TextField):
    
    def formfield(self, **kwargs):
        kwargs["widget"] = FeedbackWidget
        return super(FeedbackField, self).formfield(**kwargs)
    
class URLField(models.CharField):
    def formfield(self, **kwargs):
        kwargs["widget"] = URLWidget
        return super(URLField, self).formfield(**kwargs)