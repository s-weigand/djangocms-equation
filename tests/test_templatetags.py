# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from djangocms_equation.templatetags.djangocms_equation_tags import (
    format_float_dot_delimiter,
)
from django.test import TestCase


class TestTemplateTags(TestCase):
    def test_format_float_dot_delimiter(self):
        self.assertEqual(format_float_dot_delimiter(2.0), "2.0")
