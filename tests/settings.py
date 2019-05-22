#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from shutil import rmtree


HELPER_SETTINGS = {
    "INSTALLED_APPS": ["djangocms_text_ckeditor", "djangocms_equation"],
    "CMS_LANGUAGES": {1: [{"code": "en", "name": "English"}]},
    "LANGUAGE_CODE": "en",
    "ALLOWED_HOSTS": ["*"],
}


def run():
    from .generate_screenshot_test_report import get_screenshot_test_base_folder
    # clean screenshots from last run
    rmtree(get_screenshot_test_base_folder(), ignore_errors=True)
    # run test and generate new screenshots
    from djangocms_helper import runner

    runner.cms("djangocms_equation")


if __name__ == "__main__":
    run()
