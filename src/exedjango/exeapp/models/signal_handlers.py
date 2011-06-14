from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.auth.management import create_superuser
from django.db.models import signals
from django.dispatch import receiver


from exeapp.models import UserProfile
import os
import shutil

def create_debug_superuser(app, created_models, **kwargs):
    if settings.DEBUG and not getattr(settings, "TEST", False):
        su = auth_models.User.objects.create_superuser("admin", "admin@exe.org",
                                                  "admin")

if settings.DEBUG and not getattr(settings, "TEST", False):
    print "DISABLING SUPERUSER CREATIONG"
    signals.post_syncdb.disconnect(
        create_superuser,
        sender=auth_models,
        dispatch_uid='django.contrib.auth.management.create_superuser')
    signals.post_syncdb.connect(create_debug_superuser,
            sender=auth_models, dispatch_uid='common.models.create_testuser')
    
@receiver(signal=signals.post_save, sender=auth_models.User)
def user_post_safe(sender, instance, created, **kwargs):
    if created:
        profile, new = UserProfile.\
                    objects.get_or_create(user=instance)
        try:
            os.mkdir(profile.media_path)
        except Exception, e:
            if not getattr(settings, "TEST", False):
                raise e
        
@receiver(signal=signals.post_delete, sender=auth_models.User)
def user_post_delete(sender, instance, **kwargs):
    profile = UserProfile(user=instance)
    print profile.media_path
    shutil.rmtree(profile.media_path)
    profile.delete()
        

    