from django.db import models
from exeapp.views.blocks.widgets import *

class TitleField(models.CharField):
    
    def formfield(self, **kwargs):
        kwargs.update({"widget" : TitleWidget})
        return super(TitleField, self).formfield(**kwargs)
    
class RichTextField(models.TextField):
    
    def formfield(self, **kwargs):
        kwargs["widget"] = FreeTextWidget
        return super(RichTextField, self).formfield(**kwargs)
    
class FeedbackField(models.TextField):
    
    def formfield(self, **kwargs):
        kwargs["widget"] = FeedbackWidget
        return super(FeedbackField, self).formfield(**kwargs)