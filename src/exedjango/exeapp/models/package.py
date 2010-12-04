from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files import File

from exeapp.models.data_package import DataPackage
from exeapp.models import package_storage

import tempfile
import logging
from django.db.models.fields.files import FieldFile
from StringIO import StringIO

log = logging.getLogger(__name__)
    
class PackageManager(models.Manager):
    def create(self, title, user):
        '''creates a database entry and a persistent object'''
        p = Package(title=title, user=user)
        p.save()
        package_id = p.id
        package_storage[package_id] = DataPackage(package_id, title)
        p.save_persist()
        return p

class Package(models.Model):
    title = models.CharField(max_length=30)
    user = models.ForeignKey(User)
    data_package = models.FileField(upload_to='packages',
                        storage=default_storage, blank=True, null=True)
    objects = PackageManager()
    
    def get_data_package(self):
        if self.id not in package_storage:
            log.debug("Loading from %s" % self.data_package)
            persistent_package = DataPackage.load(self.data_package.file)
            package_storage[self.id] = persistent_package
        return package_storage[self.id]
    
    def save_persist(self):
        if self.id in package_storage:
            persistent_package = package_storage[self.id]
            file = tempfile.NamedTemporaryFile(mode="w")
            persistent_package.doSave(file)
            self.data_package.save("Package %s" % self.id, 
                                    File(open(file.name)))
            
    class Meta:
        app_label = "exeapp"
    
    def __unicode__(self):
        return "Package %s: %s" % (self.id, self.title)