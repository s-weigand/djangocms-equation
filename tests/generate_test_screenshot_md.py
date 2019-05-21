# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
from urllib.parse import quote


def get_screenshot_test_base_folder():

    tox_env_name = os.getenv("TOX_ENV_NAME", "")
    dir_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "test_screenshots", tox_env_name)
    )
    return dir_path


def generate_test_screenshot_report():
    test_env_name = os.getenv("TOX_ENV_NAME", "stand alone")
    screen_shot_dict = {}
    base_path = get_screenshot_test_base_folder()
    for root, _, filenames in os.walk(base_path):
        for filename in filenames:
            if filename.endswith(".png"):
                dirname = os.path.split(root)[-1]
                screenshot_caption = os.path.splitext(filename)[0]
                if "TRAVIS" in os.environ:
                    if not base_path.endswith(dirname):
                        screenshot_path = "./{}/{}".format(dirname, quote(filename))

                    else:
                        screenshot_path = "./{}".format(quote(filename))
                else:
                    screenshot_path = os.path.abspath(os.path.join(root, quote(filename)))
                    screenshot_path = r"file:///{}".format(screenshot_path)

                # screenshot_path = quote(screenshot_path)
                if dirname not in screen_shot_dict:
                    screen_shot_dict[dirname] = [
                        {
                            "caption": screenshot_caption,
                            "path": screenshot_path,
                            "filename": filename,
                        }
                    ]
                else:
                    screen_shot_dict[dirname] += [
                        {
                            "caption": screenshot_caption,
                            "path": screenshot_path,
                            "filename": filename,
                        }
                    ]

    report_path = os.path.join(base_path, "test_screenshots.html")
    html_img_template = r"""
<figure class="image" style="padding: 1rem;">
  <img src="{path}" alt="{filename}" style="border: solid black 1px;">
  <figcaption>{caption}</figcaption>
</figure>"""
    with open(report_path, "w+") as report:
        report.write("<h1> Screenshots of test-env: {}</h1>\n".format(test_env_name))
        for test_name, screen_shots in screen_shot_dict.items():
            report.write("\n<h2> Test: {}</h2>\n\n".format(test_name))
            screen_shots_html = map(
                lambda screen_shot: html_img_template.format(**screen_shot),
                screen_shots,
            )
            report.writelines(screen_shots_html)


if __name__ == "__main__":
    generate_test_screenshot_report()
