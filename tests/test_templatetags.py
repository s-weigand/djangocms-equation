from django.test import TestCase

from djangocms_equation.templatetags.djangocms_equation_tags import format_float_dot_delimiter


class TestTemplateTags(TestCase):
    def test_format_float_dot_delimiter(self):
        self.assertEqual(format_float_dot_delimiter(2.0), "2.0")
