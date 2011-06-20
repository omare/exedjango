from exeapp.models.idevices.idevice import Idevice

from exeapp.models.idevices.freetextidevice import FreeTextIdevice
from exeapp.models.idevices.activityidevice import ActivityIdevice

idevice_list = ['FreeTextIdevice',
            "ActivityIdevice",
            ]

__all__ = ['Idevice'] + idevice_list
           