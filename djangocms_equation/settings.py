from django.conf import settings

KATEX_EQUATION_SETTINGS = getattr(
    settings, "KATEX_EQUATION_SETTINGS", {"allow_copy": False}
)
