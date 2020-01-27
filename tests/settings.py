#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import sys
from shutil import rmtree


HELPER_SETTINGS = {
    "INSTALLED_APPS": ["djangocms_text_ckeditor", "djangocms_equation"],
    "CMS_LANGUAGES": {1: [{"code": "en", "name": "English"}]},
    "LANGUAGE_CODE": "en",
    "ALLOWED_HOSTS": ["*"],
    "CKEDITOR_SETTINGS": {
        "contentsCss": ["/static/djangocms_equation/css/change_form_template.css"]
    },
    "KATEX_EQUATION_SETTINGS": {"allow_copy": True},
}


def run():
    from .utils.generate_screenshot_test_report import get_screenshot_test_base_folder

    # clean screenshots from last run
    rmtree(get_screenshot_test_base_folder(), ignore_errors=True)
    # run test and generate new screenshots
    from app_helper import runner

    runner.cms("djangocms_equation")


def doc_setup():
    from app_helper import runner

    runner.setup('djangocms_equation', sys.modules[__name__], use_cms=True)


if __name__ == "__main__":
    run()
