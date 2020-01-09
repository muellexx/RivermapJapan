from django import forms
from .models import Section


class SectionAddForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name_jp', 'start_lat', 'start_lng', 'end_lat', 'end_lng']

