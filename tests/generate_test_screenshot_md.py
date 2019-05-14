# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os


def get_screenshot_test_base_folder():

    tox_env_name = os.getenv("TOX_ENV_NAME", "")
    dir_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "test_screenshots", tox_env_name)
    )
    return dir_path


def generate_test_screenshot_md():
    test_env_name = os.getenv("TOX_ENV_NAME", "stand alone")
    screen_shot_dict = {}
    base_path = get_screenshot_test_base_folder()
    for root, _, filenames in os.walk(base_path):
        for filename in filenames:
            if filename.endswith(".png"):
                dirname = os.path.split(root)[-1]
                screenshot_caption = os.path.splitext(filename)[0]
                if not base_path.endswith(dirname):
                    screenshot_path = "./{}/{}".format(dirname, filename)

                else:
                    screenshot_path = "./{}".format(filename)
                if not dirname in screen_shot_dict:
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

    md_path = os.path.join(base_path, "test_screenshots.md")
    md_img_template = """
| ![{filename}]({path} "{caption}") |
|:--:|
| *{caption}* |

"""
    with open(md_path, "w+") as screenshot_md:
        screenshot_md.write("# Screenshots of test-env: {}\n".format(test_env_name))
        for test_name, screen_shots in screen_shot_dict.items():
            screenshot_md.write("\n## Test: {}\n\n".format(test_name))
            screen_shots_md = map(
                lambda screen_shot: md_img_template.format(**screen_shot), screen_shots
            )
            screenshot_md.writelines(screen_shots_md)


if __name__ == "__main__":
    generate_test_screenshot_md()
