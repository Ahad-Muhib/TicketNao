from django import forms
from main.models import Operator, Bus, Route, Schedule

class OperatorForm(forms.ModelForm):
    """Form for operator management"""
    class Meta:
        model = Operator
        fields = ['name', 'description', 'logo', 'contact_email', 'contact_phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'logo': forms.URLInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BusForm(forms.ModelForm):
    """Form for bus management"""
    class Meta:
        model = Bus
        fields = ['operator', 'name', 'registration_number', 'bus_type', 'total_seats', 'amenities', 'is_active']
        widgets = {
            'operator': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bus_type': forms.Select(attrs={'class': 'form-select'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'amenities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class RouteForm(forms.ModelForm):
    """Form for route management"""
    class Meta:
        model = Route
        fields = ['source', 'destination', 'distance_km', 'estimated_duration_minutes']
        widgets = {
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'distance_km': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'estimated_duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ScheduleForm(forms.ModelForm):
    """Form for schedule management"""
    departure_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    arrival_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    
    class Meta:
        model = Schedule
        fields = ['route', 'bus', 'departure_time', 'arrival_time', 'fare', 'is_active']
        widgets = {
            'route': forms.Select(attrs={'class': 'form-select'}),
            'bus': forms.Select(attrs={'class': 'form-select'}),
            'fare': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
