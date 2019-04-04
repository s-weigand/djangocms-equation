# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys

from django.conf import settings
from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
# from cms.cms_plugins.
from djangocms_text_ckeditor.cms_plugins import Text

from .forms import EquationForm, EquationFormTextEdit
from .models import EquationPluginModel


@plugin_pool.register_plugin  # register the plugin
class EquationPlugin(CMSPluginBase):
    model = EquationPluginModel  # model where plugin data are saved
    name = _("Equation")  # name of the plugin in the interface
    change_form_template = 'djangocms_equation/change_form.html'
    render_template = "djangocms_equation/_equation_plugin.html"
    text_enabled = True
    disable_child_plugins = True
    admin_preview = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self, context, instance, placeholder):
        parent_plugin = instance.get_parent()
        if parent_plugin is not None and parent_plugin.get_plugin_name() == "Text":
            pass
        else:
            instance.is_inline = False
        context.update({"instance": instance, "placeholder": placeholder})
        return context

    def icon_src(self, instance):
        return ""

    def icon_alt(self, instance):
        return "$${tex_code}$$".format(tex_code=instance.tex_code)
