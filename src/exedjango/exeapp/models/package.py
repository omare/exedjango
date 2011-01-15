from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models.fields.files import FieldFile

from exeapp.models import DataPackage
from exeapp.models import package_storage

import tempfile
import logging
from StringIO import StringIO

log = logging.getLogger(__name__)
    
class PackageManager(models.Manager):
    def create(self, title, user):
        '''creates a database entry and a persistent object'''
        p = Package(title=title, user=user)
        p.save()
        package_id = p.id
        package_storage[package_id] = DataPackage(package_id, title)
        p.save_data_package()
        return p

class Package(models.Model):
    title = models.CharField(max_length=30)
    user = models.ForeignKey(User)
    data_package = models.FileField(upload_to='packages',
                        storage=default_storage, blank=True, null=True)
    objects = PackageManager()
    
    def get_data_package(self):
        '''Returns data_package. Loads it from file, if it's not loaded'''
        if self.id not in package_storage:
            log.debug("Loading data packge %s" % self.id)
            persistent_package = DataPackage.load(self.data_package.file)
            self.data_package.file.close()
            package_storage[self.id] = persistent_package
        return package_storage[self.id]
    
    def unload_data_package(self):
        '''Unload a data package from package store'''
        if self.id in package_storage:
            log.debug("Unloading data package %s" % self.id)
            del package_storage[self.id]
            
    def save_data_package(self):
        '''Saves the data package to file system'''
        log.debug("Saving package %s" % self.id)
        if self.id in package_storage:
            persistent_package = package_storage[self.id]
            saved_file = StringIO()
            persistent_package.doSave(saved_file)
            saved_value = saved_file.getvalue()
            saved_file.close()
            self.data_package.save("Package %s" % self.id, 
                                    ContentFile(saved_value))
            
            
    class Meta:
        app_label = "exeapp"
    
    def __unicode__(self):
        return "Package %s: %s" % (self.id, self.title)