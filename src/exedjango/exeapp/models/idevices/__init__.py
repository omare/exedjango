from exeapp.models.idevices.idevice import Idevice

from exeapp.models.idevices.freetextidevice import FreeTextIdevice
from exeapp.models.idevices.activityidevice import ActivityIdevice
from exeapp.models.idevices.glossaryidevice import GlossaryIdevice
from exeapp.models.idevices.readingactidevice import ReadingActivityIdevice
from exeapp.models.idevices.reflectionidevice import ReflectionIdevice
from exeapp.models.idevices.tocidevice import TOCIdevice
from exeapp.models.idevices.wikiidevice import WikipediaIdevice

idevice_list = [FreeTextIdevice,
            ActivityIdevice,
            GlossaryIdevice,
            ReadingActivityIdevice,
            ReflectionIdevice,
            TOCIdevice,
            WikipediaIdevice,
            ]

__all__ = ['Idevice', 'idevice_list'] +\
                    [idevice.__name__ for idevice in idevice_list]
