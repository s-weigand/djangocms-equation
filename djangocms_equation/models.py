# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin


@python_2_unicode_compatible
class EquationPluginModel(CMSPlugin):
    tex_code = models.CharField(
        _("tex_code"),
        max_length=256,
        blank=True,
    )
    is_inline = models.BooleanField(
        _("is_inline"),
        blank=True,
    )

    def __str__(self):
        if self.is_inline:
            return "${tex_code}$".format(tex_code=self.tex_code)
        else:
            return "$${tex_code}$$".format(tex_code=self.tex_code)
