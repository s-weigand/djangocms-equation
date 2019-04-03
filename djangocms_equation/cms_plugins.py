# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .forms import EquationForm
from .models import EquationPluginModel


@plugin_pool.register_plugin  # register the plugin
class GistPlugin(CMSPluginBase):
    model = EquationPluginModel  # model where plugin data are saved
    name = _("Equation")  # name of the plugin in the interface
    form = EquationForm
    change_form_template = 'djangocms_equation/change_form.html'
    render_template = "djangocms_equation/_equation_plugin.html"
    text_enabled = True

    def render(self, context, instance, placeholder):
        context.update({"instance": instance, "placeholder": placeholder})
        return context

    def icon_src(self, instance):
        return ""

    def icon_alt(self, instance):
        return "$${tex_code}$$".format(tex_code=instance.tex_code)

