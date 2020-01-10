from django import forms
from .models import Section


class SectionAddForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name_jp', 'start_lat', 'start_lng', 'end_lat', 'end_lng']
        labels = {
            "name_jp": "Name of the section"
        }


class SectionEditForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name_jp', 'name', 'observatory', 'dam', 'difficulty', 'high_water', 'middle_water', 'low_water',
                  'start_lat', 'start_lng', 'end_lat', 'end_lng']
        labels = {
            "name_jp": "Name (Japanese)",
            "name": "Name (English)",
            "difficulty": "Difficulty (from I to VI e.g. II, III+, II(III+), IV-V)"
        }

