# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from .models import EquationPluginModel

admin.site.register(EquationPluginModel, admin.ModelAdmin)
