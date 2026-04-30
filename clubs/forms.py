from django import forms

from .models import Club


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = [
            'name',
            'founded_year',
            'country',
            'city',
            'stadium',
            'coach',
            'budget',
            'logo_url',
            'trophies_count',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'founded_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'stadium': forms.TextInput(attrs={'class': 'form-control'}),
            'coach': forms.TextInput(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'logo_url': forms.TextInput(attrs={'class': 'form-control'}),
            'trophies_count': forms.NumberInput(attrs={'class': 'form-control'}),
        }
