# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
from pathlib import Path
from collections import OrderedDict

# from django.conf import settings
# from django.template.loader import render_to_string, get_template

from jinja2 import Environment, FileSystemLoader

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

UTILS_PATH = Path(__file__).parent


def get_screenshot_test_base_folder():
    if "GITHUB_WORKSPACE" in os.environ:
        tox_env_name = ""
    else:
        tox_env_name = os.getenv("TOX_ENV_NAME", "")
    dir_path = UTILS_PATH.joinpath("..", "..", "test_screenshots", tox_env_name)
    return dir_path


def generate_test_screenshot_report(file_prefix=False):
    test_env_name = os.getenv("TOX_ENV_NAME", "stand alone")
    screen_shots_dict = OrderedDict()
    base_path = get_screenshot_test_base_folder().resolve()
    for file_path in base_path.rglob("*.png"):
        browser_name, test_name, filename = list(file_path.parts)[-3:]
        screenshot_caption = os.path.splitext(filename)[0]
        if "GITHUB_WORKSPACE" in os.environ or not file_prefix:
            rel_path = (
                file_path.with_name(quote(filename)).relative_to(base_path).as_posix()
            )
            screenshot_path = "./{}".format(rel_path)
        else:
            screenshot_path = file_path.as_uri()

        if browser_name not in screen_shots_dict:
            screen_shots_dict[browser_name] = {}

        screen_shot_dict = {
            "caption": screenshot_caption,
            "path": screenshot_path,
            "filename": filename,
        }
        if test_name not in screen_shots_dict[browser_name]:
            screen_shots_dict[browser_name][test_name] = [screen_shot_dict]
        else:
            screen_shots_dict[browser_name][test_name] += [screen_shot_dict]
    report_filenames = []

    env = Environment(loader=FileSystemLoader(str(UTILS_PATH.resolve())))
    template = env.get_template("report_template.html")
    for browser_name, screen_shots_subdict in screen_shots_dict.items():
        for test_name, screen_shots in screen_shots_subdict.items():
            report_filename = "{}_{}.html".format(browser_name, test_name)
            report_path = Path(base_path) / report_filename
            context = {
                "test_name": test_name,
                "test_env_name": test_env_name,
                "browser_name": browser_name,
                "screen_shots": screen_shots,
            }

            report_string = template.render(**context)
            report_path.write_text(report_string)
            report_filenames.append(report_filename)
    return report_filenames


if __name__ == "__main__":
    generate_test_screenshot_report(False)
