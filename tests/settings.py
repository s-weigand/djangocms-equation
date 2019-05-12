#!/usr/bin/env python
# -*- coding: utf-8 -*-
HELPER_SETTINGS = {
    "INSTALLED_APPS": ["djangocms_equation"],
    "CMS_LANGUAGES": {1: [{"code": "en", "name": "English"}]},
    "LANGUAGE_CODE": "en",
    "ALLOWED_HOSTS": ["*"],
}


def run():
    from djangocms_helper import runner
    runner.cms("djangocms_equation")


if __name__ == "__main__":
    run()
