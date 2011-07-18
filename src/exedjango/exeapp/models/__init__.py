from django.contrib.auth.models import User

from exeapp.models.userprofile import UserProfile
from exeapp.models import signal_handlers



from exeapp.models import idevices
from exeapp.models.idevices import *
idevice_store = dict(((idevice.__name__, idevice) \
                      for idevice in idevice_list))


from exeapp.models.node import Node
from exeapp.models.package import Package, DublinCore
from exeapp.models.tests.test_data_package import PackageTestCase
from exeapp.models.tests.test_package import UserandPackageTestCase


__all__ = ['UserProfile',
           'Package', 'DublinCore', 'UserandPackageTestCase',
           'idevice_store', 
           'User',
           'Node',
           'idevice_store',
           ]

__all__ += idevices.__all__

