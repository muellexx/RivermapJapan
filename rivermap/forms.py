from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms
from .models import Section


class SectionAddForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name_jp', 'lat', 'lng', 'end_lat', 'end_lng']
        labels = {
            "name_jp": "Name of the section",
            "lat": "Start Lat",
            "lng": "Start Lng"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name_jp',
            Row(
                Column('lat', css_class='form-group col-md-6 mb-0'),
                Column('lng', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('end_lat', css_class='form-group col-md-6 mb-0'),
                Column('end_lng', css_class='form-group col-md-6 mb-0'),
            ),
            Submit('submit', 'Add Section')
        )


class SectionEditForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name_jp', 'name', 'observatory', 'dam', 'content', 'difficulty', 'high_water', 'middle_water',
                  'low_water', 'lat', 'lng', 'end_lat', 'end_lng']
        labels = {
            "name_jp": "Name (Japanese)",
            "name": "Name (English)",
            "lat": "Start Lat",
            "lng": "Start Lng",
            "content": "Useful Information:",
            "difficulty": "Difficulty (from I to VI e.g. II, III+, II(III+), IV-V)"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name_jp', css_class='form-group col-md-6 mb-0'),
                Column('name', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('observatory', css_class='form-group col-md-6 mb-0'),
                Column('dam', css_class='form-group col-md-6 mb-0'),
            ),
            'content',
            Row(
                Column('difficulty', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('low_water', css_class='form-group col-md-4 mb-0'),
                Column('middle_water', css_class='form-group col-md-4 mb-0'),
                Column('high_water', css_class='form-group col-md-4 mb-0'),
            ),
            Row(
                Column('lat', css_class='form-group col-md-6 mb-0'),
                Column('lng', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('end_lat', css_class='form-group col-md-6 mb-0'),
                Column('end_lng', css_class='form-group col-md-6 mb-0'),
            ),
            Submit('submit', 'Save Section')
        )

