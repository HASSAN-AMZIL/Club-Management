from django import forms

from .models import Player, Stats


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = [
            'name',
            'age',
            'position',
            'value',
            'join_date',
            'image_url',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'join_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'image_url': forms.TextInput(attrs={'class': 'form-control'}),
        }


class StatsForm(forms.ModelForm):
    class Meta:
        model = Stats
        fields = [
            'pace',
            'shooting',
            'passing',
            'defense',
            'dribbling',
        ]
        widgets = {
            'pace': forms.NumberInput(attrs={'class': 'form-control'}),
            'shooting': forms.NumberInput(attrs={'class': 'form-control'}),
            'passing': forms.NumberInput(attrs={'class': 'form-control'}),
            'defense': forms.NumberInput(attrs={'class': 'form-control'}),
            'dribbling': forms.NumberInput(attrs={'class': 'form-control'}),
        }
