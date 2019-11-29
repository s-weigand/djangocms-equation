# -*- coding: utf-8 -*-
"""
Inputs which are used in the Equation editing dialog.
"""

# http://docs.django-cms.org/en/latest/reference/plugins.html

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import EquationPluginModel, ALLOWED_FONT_SIZE_UNITS


class EquationForm(forms.ModelForm):
    """
    Inputs which are used in the Equation editing dialog.
    """

    tex_code = forms.CharField(
        help_text=_("Insert your LaTeX code here."),
        widget=forms.Textarea(attrs={"rows": "2", "spellcheck": "false"}),
    )
    """
    Input Textarea for the Latex code of the equation.
    """
    is_inline = forms.BooleanField(
        help_text=_(
            "Select if the equation should be inline (only effects elements in the text editor)."
        ),
        required=False,
        widget=forms.CheckboxInput,
    )
    """
    Input checkbox for the value of is_inline.
    """
    font_size_value = forms.FloatField(
        help_text=_("Value of the font-size to be used for the equation."),
        widget=forms.NumberInput(
            attrs={"step": "0.1", "id": "djangocms_equation_font_size_value"}
        ),
        initial=1,
        min_value=0.01,
        required=True,
    )
    """
    Input spinner for the value of font-size.
    """
    font_size_unit = forms.ChoiceField(
        help_text=_("Unit of the font-size to be used for the equation."),
        choices=ALLOWED_FONT_SIZE_UNITS,
        initial="rem",
        required=True,
        widget=forms.Select(attrs={"id": "djangocms_equation_font_size_unit"}),
    )
    """
    Input Select for the value of the fontsize unit.
    """

    class Meta:
        """
        Needed so the form gets rendered properly my django-cms
        """

        model = EquationPluginModel
        fields = ["tex_code", "is_inline", "font_size_value", "font_size_unit"]
