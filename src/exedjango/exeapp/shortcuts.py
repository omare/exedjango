from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

from exeapp.models import Package
from exedjango.base.http import Http403

def get_package_by_id_or_error(func):
    '''Works on views with package_id argument.
Raises 403 if a package doesn't belong to the user or 404 the package
can't be found. 
Please specify additional view arguments in the view docstring.
Depends on Http403 handling middleware.
Tested by exeapp.tests.ShortcutsTestCase.test_get_package_or_error. '''
    def permission_checking_view(request, package_id, *args, **kwargs):
        try:
            # assume we got a standard rpc package view
            package = Package.objects.get(id=package_id)
        except ObjectDoesNotExist:
            raise Http404
        if package.user.username == request.user.username:
            return func(request, package, *args, **kwargs)
        else:
            raise Http403
    # Set docstring and name
    permission_checking_view.__name__ = func.__name__
    permission_checking_view.__doc__ = \
'''Wrapped by exeapp.shortcuts.get_package_by_id_or_error.
Original docstring:
%s''' % func.__doc__
    return permission_checking_view