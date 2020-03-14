from functools import partial
from itertools import groupby
from operator import attrgetter

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from .models import Prefecture, Section, MapObjectComment, River, Spot


class GroupedModelChoiceIterator(forms.models.ModelChoiceIterator):
    def __init__(self, field, groupby):
        self.groupby = groupby
        super().__init__(field)

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        queryset = self.queryset
        # Can't use iterator() when queryset uses prefetch_related()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for group, objs in groupby(queryset, self.groupby):
            yield (group, [self.choice(obj) for obj in objs])


class GroupedModelChoiceField(forms.models.ModelChoiceField):
    def __init__(self, *args, choices_groupby, **kwargs):
        if isinstance(choices_groupby, str):
            choices_groupby = attrgetter(choices_groupby)
        elif not callable(choices_groupby):
            raise TypeError('choices_groupby must either be a str or a callable accepting a single argument')
        self.iterator = partial(GroupedModelChoiceIterator, groupby=choices_groupby)
        super().__init__(*args, **kwargs)


class ObjectAddForm(forms.ModelForm):
    type_choices = [(1, 'Section'), (2, 'Spot')]
    object_type = forms.ChoiceField(choices=type_choices)
    prefecture = GroupedModelChoiceField(
        queryset=Prefecture.objects.all(),
        choices_groupby='region',
        empty_label=None,
        to_field_name="slug"
    )

    class Meta:
        model = Prefecture
        fields = ['prefecture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('object_type'),
                Column('prefecture'),
            ),
            Submit('add_object', _('Next'))
        )


class SectionAddForm(forms.ModelForm):

    class Meta:
        model = Section
        fields = ['name_jp', 'lat', 'lng', 'end_lat', 'end_lng', 'prefecture', 'river']
        widgets = {"prefecture": forms.HiddenInput()}
        labels = {
            "name_jp": _('Name of the Section'),
            "lat": _('Start Latitude'),
            "lng": _('Start Longitude'),
            "end_lat": _('End Latitude'),
            "end_lng": _('End Longitude')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['river'] = forms.ModelChoiceField(River.objects.all(), empty_label=None)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'prefecture',
            Row(
                Column('name_jp', css_class='form-group col-md-6 col-12 mb-0'),
                Column('river', css_class='form-group col-md-6 col-12 mb-0'),
            ),
            HTML(_('Click on the map twice to add the Section')),
            Row(css_id='map-small'),
            Row(
                Column('lat', css_class='form-group col-sm-6 col-12 mb-0'),
                Column('lng', css_class='form-group col-sm-6 col-12 mb-0'),
            ),
            Row(
                Column('end_lat', css_class='form-group col-sm-6 col-12 mb-0'),
                Column('end_lng', css_class='form-group col-sm-6 col-12 mb-0'),
            ),

            Submit('add_section', _('Add Section'))
        )


class SpotAddForm(forms.ModelForm):

    class Meta:
        model = Spot
        fields = ['name_jp', 'lat', 'lng', 'prefecture', 'river']
        widgets = {"prefecture": forms.HiddenInput()}
        labels = {
            "name_jp": _('Name of the Spot'),
            "lat": _('Latitude'),
            "lng": _('Longitude')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['river'] = forms.ModelChoiceField(River.objects.all(), empty_label=None)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'prefecture',
            Row(
                Column('name_jp', css_class='form-group col-md-6 col-12 mb-0'),
                Column('river', css_class='form-group col-md-6 col-12 mb-0'),
            ),
            HTML(_('Click on the map to add the Spot')),
            Row(css_id='map-small'),
            Row(
                Column('lat', css_class='form-group col-sm-6 col-12 mb-0'),
                Column('lng', css_class='form-group col-sm-6 col-12 mb-0'),
            ),

            Submit('add_spot', _('Add Spot'))
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
            HTML(_('Click on the map twice to add the new Coordinates of the Section')),
            Row(css_id='map-small'),
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


class SpotEditForm(forms.ModelForm):
    class Meta:
        model = Spot
        fields = ['name_jp', 'name', 'observatory', 'dam', 'content', 'difficulty', 'high_water', 'middle_water',
                  'low_water', 'lat', 'lng']
        labels = {
            "name_jp": _('Name (Japanese)'),
            "name": _('Name (English)'),
            "observatory": _('Observatory'),
            "dam": pgettext_lazy('form', 'Dam'),
            "lat": _('Latitude'),
            "lng": _('Longitude'),
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
            HTML(_('Click on the map to add the new Coordinates of the Spot')),
            Row(css_id='map-small'),
            Row(
                Column('lat', css_class='form-group col-sm-6 col-12 mb-0'),
                Column('lng', css_class='form-group col-sm-6 col-12 mb-0'),
            ),
            Submit('submit', _('Save Spot'))
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
