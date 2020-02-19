from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from .models import Section, MapObjectComment


class SectionAddForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name_jp', 'lat', 'lng', 'end_lat', 'end_lng']
        labels = {
            "name_jp": _('Name of the section'),
            "lat": _('Start Latitude'),
            "lng": _('Start Longitude'),
            "end_lat": _('End Latitude'),
            "end_lng": _('End Longitude')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name_jp',
            Row(css_id='map-small'),
            Row(
                Column('lat', css_class='form-group col-md-6 mb-0'),
                Column('lng', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('end_lat', css_class='form-group col-md-6 mb-0'),
                Column('end_lng', css_class='form-group col-md-6 mb-0'),
            ),

            Submit('submit', _('Add Section'))
        )


class SectionEditForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name_jp', 'name', 'observatory', 'dam', 'content', 'difficulty', 'high_water', 'middle_water',
                  'low_water', 'lat', 'lng', 'end_lat', 'end_lng']
        labels = {
            "name_jp": _('Name (Japanese)'),
            "name": _('Name (English)'),
            "observatory": _('Observatory'),
            "dam": pgettext_lazy('form', 'Dam'),
            "lat": _('Start Latitude'),
            "lng": _('Start Longitude'),
            "end_lat": _('End Latitude'),
            "end_lng": _('End Longitude'),
            "content": _('Useful Information:'),
            "difficulty": _('Difficulty (from I to VI e.g. II, III+, II(III+), IV-V)'),
            "low_water": _('Low Water'),
            "middle_water": _('Middle Water'),
            "high_water": _('High Water')
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
            Submit('submit', _('Save Section'))
        )


class CommentAddForm(forms.ModelForm):
    class Meta:
        model = MapObjectComment
        fields = ['title', 'content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'content',
            Submit('submit', 'Post')
        )
