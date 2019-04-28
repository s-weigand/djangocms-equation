#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `djangocms_equation` package."""

# from djangocms_equation.cms_plugins import EquationPlugin


# from django.test import TestCase
# from django.test.client import RequestFactory

# from cms.api import add_plugin
# from cms.models import Placeholder
# from cms.plugin_rendering import ContentRenderer

# from djangocms_equation.cms_plugins import EquationPlugin
# from djangocms_equation.models import EquationPluginModel

# class MypluginTests(TestCase):
#     def test_plugin_context(self):
#         placeholder = Placeholder.objects.create(slot='test')
#         model_instance = add_plugin(
#             placeholder,
#             EquationPlugin,
#             'en',
#         )
#         plugin_instance = model_instance.get_plugin_class_instance()
#         context = plugin_instance.render({}, model_instance, None)
#         self.assertIn('key', context)
#         self.assertEqual(context['key'], 'value')

#     def test_plugin_html(self):
#         placeholder = Placeholder.objects.create(slot='test')
#         model_instance = add_plugin(
#             placeholder,
#             EquationPlugin,
#             'en',
#         )
#         renderer = ContentRenderer(request=RequestFactory())
#         html = renderer.render_plugin(model_instance, {})
#         self.assertEqual(html, '<strong>Test</strong>')
