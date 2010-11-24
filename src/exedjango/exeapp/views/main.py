from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from exeapp.models import Package, User
from exeapp.forms import CreatePackageForm


@login_required
def main(request):
    user = User.objects.get(username=request.user.username)
    package_list = Package.objects.filter(user=user)
    create_package_form = CreatePackageForm()
    return render_to_response('main.html', locals())

def create_package(request):
    if request.method == 'POST':
        form = CreatePackageForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=request.user.username)
            cd = form.cleaned_data
            Package.objects.create(title=cd['package_title'], user=user)
    return redirect('/exeapp/main/')

