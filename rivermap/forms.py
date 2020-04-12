from functools import partial
from itertools import groupby
from operator import attrgetter

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field, Div
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
    type_choices = [(1, pgettext_lazy('form', 'Section')), (2, pgettext_lazy('form', 'Spot'))]
    object_type = forms.ChoiceField(choices=type_choices, label=_('Object Type'))
    prefecture = GroupedModelChoiceField(
        queryset=Prefecture.objects.all(),
        choices_groupby='region',
        empty_label=None,
        to_field_name="slug",
        label=pgettext_lazy('form', 'Prefecture')
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
            "end_lng": _('End Longitude'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['river'] = forms.ModelChoiceField(River.objects.all(), empty_label=None, label=pgettext_lazy('form', 'River'))
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
        self.fields['river'] = forms.ModelChoiceField(River.objects.all(), empty_label=None, label=pgettext_lazy('form', 'River'))
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
    diff_choices = [('None', '----------'), ('I', 'I'), ('I+', 'I+'), ('I-II', 'I-II'), ('II-', 'II-'),
                    ('II', 'II'), ('II+', 'II+'), ('II-III', 'II-III'), ('III-', 'III-'),
                    ('III', 'III'), ('III+', 'III+'), ('III-IV', 'III-IV'), ('IV-', 'IV-'),
                    ('IV', 'IV'), ('IV+', 'IV+'), ('IV-V', 'IV-V'), ('V-', 'V-'),
                    ('V', 'V'), ('V+', 'V+'), ('V-VI', 'V-VI'), ('VI-', 'VI-'), ('VI', 'VI')]
    average_difficulty = forms.ChoiceField(choices=diff_choices, required=False, label=_('Average Difficulty (Middle Water)'))
    max_difficulty = forms.ChoiceField(choices=diff_choices, required=False, label=_('Max Difficulty (Middle Water)'))

    class Meta:
        model = Section
        fields = ['name_jp', 'name', 'observatory', 'dam', 'content', 'high_water', 'middle_water',
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
            "low_water": _('Low Water'),
            "middle_water": _('Middle Water'),
            "high_water": _('High Water')
        }

    def is_valid(self):
        valid = super(SectionEditForm, self).is_valid()
        if not valid:
            return valid
        cleaned_average = self.cleaned_data['average_difficulty']
        cleaned_max = self.cleaned_data['max_difficulty']
        if cleaned_max == 'None':
            return True
        if cleaned_average == 'None':
            self.add_error('average_difficulty', _('Average Difficulty has to be chosen to set Max Difficulty'))
            return False
        index_average = self.diff_choices.index((cleaned_average, cleaned_average))
        index_max = self.diff_choices.index((cleaned_max, cleaned_max))
        if not index_max >= index_average:
            self.add_error('max_difficulty', _('Max Difficulty cannot be smaller than Average Difficulty'))
            return False
        return True

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
                Column('average_difficulty', css_class='form-group col-md-6 col-12 mb-0'),
                Column('max_difficulty', css_class='form-group col-md-6 col-12 mb-0'),
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
    diff_choices = [('None', '----------'), ('I', 'I'), ('I+', 'I+'), ('I-II', 'I-II'), ('II-', 'II-'),
                    ('II', 'II'), ('II+', 'II+'), ('II-III', 'II-III'), ('III-', 'III-'),
                    ('III', 'III'), ('III+', 'III+'), ('III-IV', 'III-IV'), ('IV-', 'IV-'),
                    ('IV', 'IV'), ('IV+', 'IV+'), ('IV-V', 'IV-V'), ('V-', 'V-'),
                    ('V', 'V'), ('V+', 'V+'), ('V-VI', 'V-VI'), ('VI-', 'VI-'), ('VI', 'VI')]
    average_difficulty = forms.ChoiceField(choices=diff_choices, required=False, label=_('Difficulty (Middle Water)'))

    class Meta:
        model = Spot
        fields = ['name_jp', 'name', 'observatory', 'dam', 'content', 'high_water', 'middle_water',
                  'low_water', 'lat', 'lng']
        labels = {
            "name_jp": _('Name (Japanese)'),
            "name": _('Name (English)'),
            "observatory": _('Observatory'),
            "dam": pgettext_lazy('form', 'Dam'),
            "lat": _('Latitude'),
            "lng": _('Longitude'),
            "content": _('Useful Information:'),
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
                Column('average_difficulty', css_class='form-group col-md-6 mb-0'),
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
        fields = ['title', 'content', 'image1', 'image2', 'image3', 'image4', 'parent']
        labels = {
            "title": _('Title'),
            "content": _('Content'),
            "image1": _('Image 1'),
            "image2": _('Image 2'),
            "image3": _('Image 3'),
            "image4": _('Image 4')
        }
        widgets = {"parent": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'content',
            'parent',
            Field('image1', oninput="showNextImage(1)"),
            Div(Field('image2', oninput="showNextImage(2)"), id="hide_div_image2", style="display: none;"),
            Div(Field('image3', oninput="showNextImage(3)"), id="hide_div_image3", style="display: none;"),
            Div(Field('image4'), id="hide_div_image4", style="display: none;"),
            Row(
                HTML('<buton id="sb-new-comment-cancel" type="hidden" class="btn btn-primary" style="margin-right: 10px" onclick="newCommentCancel()">Cancel</buton>'),
                Submit('submit', _('Post'))
            )
        )
