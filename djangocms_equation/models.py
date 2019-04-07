# -*- coding: utf-8 -*-

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


@python_2_unicode_compatible
class EquationPluginModel(CMSPlugin):
    tex_code = models.CharField(_("tex_code"), max_length=256, blank=True)
    is_inline = models.BooleanField(_("is_inline"), blank=True)

    font_size_value = models.FloatField(_("font_size_value"), default=1, )
    font_size_unit = models.CharField(
        _("font_size_unit"),
        max_length=5,
        choices=ALLOWED_FONT_SIZE_UNITS,
    )

    def __str__(self):
        if self.is_inline:
            return "${tex_code}$".format(tex_code=self.tex_code)
        else:
            return "$${tex_code}$$".format(tex_code=self.tex_code)
