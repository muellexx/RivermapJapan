from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Submit, Field, Div
from django import forms
from django.utils.translation import gettext_lazy as _

from blog.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image1', 'image2', 'image3', 'image4']
        labels = {
            "title": _('Title'),
            "content": _('Content'),
            "image1": _('Image 1'),
            "image2": _('Image 2'),
            "image3": _('Image 3'),
            "image4": _('Image 4')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'content',
            Field('image1', oninput="showNextImage(1)"),
            Div(Field('image2', oninput="showNextImage(2)"), id="hide_div_image2", style="display: none;"),
            Div(Field('image3', oninput="showNextImage(3)"), id="hide_div_image3", style="display: none;"),
            Div(Field('image4'), id="hide_div_image4", style="display: none;"),
            Row(
                Submit('submit', _('Post'))
            )
        )
