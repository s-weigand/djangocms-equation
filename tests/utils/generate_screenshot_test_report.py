# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
from collections import OrderedDict

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


def get_screenshot_test_base_folder():
    if "GITHUB_WORKSPACE" in os.environ:
        tox_env_name = ""
    else:
        tox_env_name = os.getenv("TOX_ENV_NAME", "")
    dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "..", "test_screenshots", tox_env_name
        )
    )
    return dir_path


def generate_test_screenshot_report(file_prefix=False):
    test_env_name = os.getenv("TOX_ENV_NAME", "stand alone")
    screen_shot_dict = OrderedDict()
    base_path = get_screenshot_test_base_folder()
    for root, _, filenames in os.walk(base_path):
        for filename in sorted(filenames):
            if filename.endswith(".png"):
                sub_root, test_name = os.path.split(root)
                _, browser_name = os.path.split(sub_root)
                screenshot_caption = os.path.splitext(filename)[0]
                if "GITHUB_WORKSPACE" in os.environ or file_prefix:
                    if not base_path.endswith(test_name):
                        screenshot_path = "./{}/{}/{}".format(
                            browser_name, test_name, quote(filename)
                        )

                    else:
                        screenshot_path = "./{}/{}".format(
                            browser_name, quote(filename)
                        )
                else:
                    screenshot_path = os.path.abspath(
                        os.path.join(root, quote(filename))
                    )
                    screenshot_path = r"file:///{}".format(screenshot_path)

                if browser_name not in screen_shot_dict:
                    screen_shot_dict[browser_name] = {}

                if test_name not in screen_shot_dict[browser_name]:
                    screen_shot_dict[browser_name][test_name] = [
                        {
                            "caption": screenshot_caption,
                            "path": screenshot_path,
                            "filename": filename,
                        }
                    ]
                else:
                    screen_shot_dict[browser_name][test_name] += [
                        {
                            "caption": screenshot_caption,
                            "path": screenshot_path,
                            "filename": filename,
                        }
                    ]

    html_img_template = r"""
<figure class="image" style="padding: 1rem;">
  <figcaption><h3>{caption}</h3></figcaption>
  <img src="{path}" alt="{filename}" style="border: solid black 1px;">
</figure>"""
    report_filenames = []

    if "GITHUB_WORKSPACE" in os.environ or file_prefix:
        for browser_name, screen_shots_subdict in screen_shot_dict.items():
            for test_name, screen_shots in screen_shots_subdict.items():
                report_filename = "{}_{}.html".format(browser_name, test_name)
                report_path = os.path.join(base_path, report_filename)
                report_title = "<h1> Screenshots of test-env: {} <br>browser: {}</h1>\n".format(
                    test_env_name, browser_name
                )
                with open(report_path, "w+") as report:
                    report.write(report_title)
                    report.write("\n<h2> Test: {}</h2>\n\n".format(test_name))
                    screen_shots_html = map(
                        lambda screen_shot: html_img_template.format(**screen_shot),
                        screen_shots,
                    )
                    report.writelines(screen_shots_html)
                report_filenames.append(report_filename)
        return report_filenames

    else:
        report_path = os.path.join(base_path, "test_screenshots.html")
        with open(report_path, "w+") as report:
            for browser_name, screen_shots_subdict in screen_shot_dict.items():
                report_title = "<h1> Screenshots of test-env: {} <br>browser: {}</h1>\n".format(
                    test_env_name, browser_name
                )
                report.write(report_title)
                for test_name, screen_shots in screen_shots_subdict.items():
                    report.write("\n<h2> Test: {}</h2>\n\n".format(test_name))
                    screen_shots_html = map(
                        lambda screen_shot: html_img_template.format(**screen_shot),
                        screen_shots,
                    )
                    report.writelines(screen_shots_html)
        return [report_path]


if __name__ == "__main__":
    generate_test_screenshot_report(True)
