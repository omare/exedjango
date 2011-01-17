from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models.fields.files import FieldFile

from exeapp.models import DataPackage

import tempfile
import logging
from StringIO import StringIO

log = logging.getLogger(__name__)
    
class PackageManager(models.Manager):
    def create(self, title, user):
        '''creates a database entry'''
        p = Package(title=title, user=user)
        p.save()
        DataPackage.objects.create(title=title, package=p)
        return p

class Package(models.Model):
    title = models.CharField(max_length=30)
    user = models.ForeignKey(User)
    objects = PackageManager()
    
    def get_data_package(self):
        '''Returns data_package.'''
        return self.data_package.all()[0]
    
    class Meta:
        app_label = "exeapp"
    
    def __unicode__(self):
        return "Package %s: %s" % (self.id, self.title)