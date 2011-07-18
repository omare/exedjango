from exeapp.models.idevices.idevice import Idevice

from exeapp.models.idevices.freetextidevice import FreeTextIdevice
from exeapp.models.idevices.activityidevice import ActivityIdevice
from exeapp.models.idevices.glossaryidevice import GlossaryIdevice

idevice_list = ['FreeTextIdevice',
            'ActivityIdevice',
            'GlossaryIdevice'
            ]

__all__ = ['Idevice'] + idevice_list
           