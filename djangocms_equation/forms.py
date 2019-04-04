# -*- coding: utf-8 -*-

# http://docs.django-cms.org/en/latest/reference/plugins.html

from django import forms

from .models import EquationPluginModel


class EquationForm(forms.ModelForm):
    tex_code = forms.CharField(widget=forms.Textarea(attrs={'rows': '2'}))
    # is_inline = forms.BooleanField()

    class Meta:
        model = EquationPluginModel
        fields = ["tex_code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EquationFormTextEdit(EquationForm):
    is_inline = forms.BooleanField(required=False, widget=forms.CheckboxInput)

    class Meta:
        model = EquationPluginModel
        fields = ["tex_code", "is_inline"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
