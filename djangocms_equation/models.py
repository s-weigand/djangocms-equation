# -*- coding: utf-8 -*-
"""
Database models for djangocms-equation.
"""
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin


ALLOWED_FONT_SIZE_UNITS = (
    ("cm", "cm"),
    ("mm", "mm"),
    ("in", "in"),
    ("px", "px"),
    ("pt", "pt"),
    ("pc", "pc"),
    ("em", "em"),
    ("ex", "ex"),
    ("ch", "ch"),
    ("rem", "rem"),
    ("vw", "vw"),
    ("vh", "vh"),
    ("vmin", "vmin"),
    ("vmax", "vmax"),
    ("%", "%"),
)
"""
Allowed values for font-size units see https://www.w3schools.com/cssref/pr_font_font-size.asp
"""


@python_2_unicode_compatible
class EquationPluginModel(CMSPlugin):
    """
    Database model of saved Equations.
    """

    tex_code = models.TextField(_("tex_code"), blank=True)
    """
    Latex code of the equation.
    """
    is_inline = models.BooleanField(_("is_inline"), blank=True)
    """
    If it should be displayed inline or be stand alone.
    """

    font_size_value = models.FloatField(_("font_size_value"), default=1)
    """
    Value of the font-size with unit font_size_unit.
    """
    font_size_unit = models.CharField(
        _("font_size_unit"), max_length=5, choices=ALLOWED_FONT_SIZE_UNITS
    )
    """
    Value of the font-size with size value font_size_value.
    """

    def __str__(self):
        """
        Returns string representation of the Equation

        Returns
        -------
        str
            String representation of the Equation
        """
        if self.is_inline:
            return "${tex_code}$".format(tex_code=self.tex_code)
        else:
            return "$${tex_code}$$".format(tex_code=self.tex_code)
