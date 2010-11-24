from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files import File

from exeapp.models.persistent_package import Package as persist_Package
from exeapp.models import package_store

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
        package_store[package_id] = persist_Package(package_id, title)
        #file = tempfile.NamedTemporaryFile(mode='w')
        #file.close()
        #package = persist_Package(package_id, title, file.name)
        #package.save(filename=file.name)
        #p.persist_file.save("Package %s" % package_id, File(open(file.name)))
        #p.save()
        
    
    
class Package(models.Model):
    title = models.CharField(max_length=30)
    user = models.ForeignKey(User)
    persist_file = models.FileField(upload_to='packages',
                        storage=default_storage, blank=True, null=True)
    objects = PackageManager()
    
    def get_persist_package(self):
        if self.id not in package_store:
            log.debug("Loading from %s" % self.persist_file)
            persistent_package = persist_Package.load(self.persist_file.file)
            package_store[self.id] = persistent_package
        return package_store[self.id]
    
    def save_persist(self):
        if self.id in package_store:
            persistent_package = package_store[self.id]
            file = tempfile.NamedTemporaryFile(mode="w")
            persistent_package.doSave(file)
            self.persist_file.save("Package %s" % self.id, 
                                    File(open(file.name)))
            
    class Meta:
        app_label = "exeapp"
    
    def __unicode__(self):
        return "Package %s: %s" % (self.id, self.title)