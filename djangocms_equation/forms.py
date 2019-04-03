# -*- coding: utf-8 -*-

# http://docs.django-cms.org/en/latest/reference/plugins.html

from django import forms

from .models import EquationPluginModel


class EquationForm(forms.ModelForm):
    tex_code = forms.CharField(widget=forms.Textarea(attrs={'rows': '5'}))

    class Meta:
        model = EquationPluginModel
        fields = ["tex_code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.tex_code.widget_attrs.({'rows': '5'})
