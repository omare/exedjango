from exeapp.models import Package
from exeapp.views.export.websiteexport import WebsiteExport

data = Package.objects.get(id=3).get_data_package()
we = WebsiteExport(data)