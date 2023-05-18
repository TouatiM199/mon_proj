from django import forms
from .models import Signature #,Certificate
class SelectSignatureForm(forms.Form):
    signature = forms.ModelChoiceField(queryset=Signature.objects.all())



class DateRangeForm(forms.Form):
    start_date = forms.DateField(label="Date de début", widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label="Date de fin", widget=forms.widgets.DateInput(attrs={'type': 'date'}))
