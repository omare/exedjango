'''
Handles registration of a new user
'''

from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.forms import UserCreationForm

def register(request):
    '''Serves a registration view or handles a POST request. Based on
    registration example from djangobook.com'''
    
    

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/exeapp/")
    else:
        form = UserCreationForm()

    return render_to_response("registration/register.html", {
        'form' : form})