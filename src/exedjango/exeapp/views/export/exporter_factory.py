from exeapp.views.export.websiteexport import WebsiteExport
from exeapp.views.export.imsexport import IMSExport
from exeapp.views.export.scormexport import ScormExport, ScormExport12,\
    CommonCartridge, ScormExport2004

exporter_map = {"website" : WebsiteExport,
                "ims" : IMSExport,
                "scorm12" : ScormExport12,
                "commoncartridge" : CommonCartridge,
                "scorm2004" : ScormExport2004,
                }

def exporter_factory(exporter_type, package, file_obj):
    if exporter_type in exporter_map:
        return exporter_map[exporter_type](package, file_obj)
    else:
        raise KeyError("Exporter type not found")
    