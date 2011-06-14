from django.db import models
from django.contrib.auth.models import User
import os
from django.conf import settings
from django.core.urlresolvers import reverse

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    
    @property
    def media_path(self):
        return os.path.join(settings.MEDIA_ROOT,
                            "uploads",
                            self.user.username)
    @property
    def media_url(self):
        return "%suploads/%s/" % (settings.MEDIA_URL, self.user.username)
    
    class Meta:
        app_label = "exeapp"