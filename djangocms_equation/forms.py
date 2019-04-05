# -*- coding: utf-8 -*-

# http://docs.django-cms.org/en/latest/reference/plugins.html

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import EquationPluginModel


class EquationForm(forms.ModelForm):
    tex_code = forms.CharField(
        help_text=_("Insert you LaTeX code here."),
        widget=forms.Textarea(attrs={"rows": "2"}),
    )
    is_inline = forms.BooleanField(
        help_text=_("Select if the equation should be inline."),
        required=False,
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = EquationPluginModel
        fields = ["tex_code", "is_inline"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
