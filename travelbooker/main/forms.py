from django import forms
from .models import Route, Schedule

class SearchForm(forms.Form):
    """Form for searching bus schedules"""
    source = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter source city'})
    )
    destination = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter destination city'})
    )
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
