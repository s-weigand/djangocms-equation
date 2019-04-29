# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .forms import EquationForm
from .models import EquationPluginModel


@plugin_pool.register_plugin  # register the plugin
class EquationPlugin(CMSPluginBase):
    model = EquationPluginModel  # model where plugin data are saved
    name = _("Equation")  # name of the plugin in the interface
    form = EquationForm
    change_form_template = "djangocms_equation/change_form.html"
    render_template = "djangocms_equation/_equation_plugin.html"
    text_enabled = True
    text_editor_preview = True
    disable_child_plugins = True
    admin_preview = True

    def render(self, context, instance, placeholder):
        """
        Method that renders the Plugin with self.render_template and
        the data in instance

        Parameters
        ----------
        context : dict
            [description]
        instance : EquationPluginModel
            Instance of the plugins Model
        placeholder : str
            [description]

        Returns
        -------
        dict
            [description]
        """

        if not self.is_in_text_editor(instance):
            instance.is_inline = False
        context.update({"instance": instance, "placeholder": placeholder})
        return context

    def icon_src(self, instance):
        return "djangocms_equation/img/LaTeX_logo.svg"

    def icon_alt(self, instance):
        if self.is_in_text_editor(instance) and instance.is_inline:
            format_str = "${tex_code}$"
        else:
            format_str = "$${tex_code}$$"
        return format_str.format(tex_code=instance.tex_code)

    def is_in_text_editor(self, instance):
        """
        Method to check if the plugin was added to a text plugin ('djangocms-text-ckeditor')
        or to page as stand alone element.

        Parameters
        ----------
        instance : EquationPluginModel
            Instance of the plugins Model

        Returns
        -------
        bool:
            True if the plugin was added to a text plugin ('djangocms-text-ckeditor')
            or False if it was added to page as stand alone element.
        """
        parent_plugin = instance.get_parent()
        if parent_plugin is not None and parent_plugin.get_plugin_name() == "Text":
            return True
        else:
            return False
