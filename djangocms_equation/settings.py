# -*- coding: utf-8 -*-
"""
Plugin specific settings with their default value.
"""
from django.conf import settings

KATEX_EQUATION_SETTINGS = getattr(
    settings, "KATEX_EQUATION_SETTINGS", {"allow_copy": False}
)
"""Default seetings of KATEX_EQUATION_SETTINGS"""
