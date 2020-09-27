from django.test import TestCase
from mixer.backend.django import mixer


class TestModel(TestCase):
    def test_create_equation_inline(self):
        equation = mixer.blend(
            "djangocms_equation.EquationPluginModel",
            tex_code=r"\int^{a}_{b}",
            is_inline=True,
            font_size_value=1,
            font_size_unit="rem",
        )
        self.assertEqual(equation.__str__(), r"$\int^{a}_{b}$")

    def test_create_equation_not_inline(self):
        equation = mixer.blend(
            "djangocms_equation.EquationPluginModel",
            tex_code=r"\int^{a}_{b}",
            is_inline=False,
            font_size_value=1,
            font_size_unit="rem",
        )
        self.assertEqual(equation.__str__(), r"$$\int^{a}_{b}$$")
