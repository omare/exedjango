from django import forms

class CreatePackageForm(forms.Form):
    package_title = forms.CharField()
    