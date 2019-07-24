# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
import socket

from django.conf import settings


from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import JavascriptException
from urllib3.exceptions import NewConnectionError, MaxRetryError

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

import percy
from six.moves.urllib.parse import quote

from .generate_screenshot_test_report import get_screenshot_test_base_folder


class DockerNotFoundException(Exception):
    pass


class InvalidBrowserNameException(Exception):
    pass


def screen_shot_path(filename, browser_name, sub_dir=""):
    base_folder = get_screenshot_test_base_folder()
    dir_path = os.path.join(base_folder, browser_name, sub_dir)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    return os.path.join(dir_path, filename)


def get_browser_instance(
    browser_port, desire_capabilities, interactive=False, browser_name="Chrome"
):
    if browser_name not in ["Chrome", "FireFox"]:
        raise InvalidBrowserNameException(
            "Only the browser_names 'Chrome' and 'FireFox' are supported"
        )
    if interactive and browser_name == "FireFox" and "TRAVIS" not in os.environ:
        return Firefox(
            executable_path=GeckoDriverManager().install(),
            desired_capabilities=DesiredCapabilities.FIREFOX,
        )
    elif interactive and "TRAVIS" not in os.environ:
        return Chrome(
            ChromeDriverManager().install(),
            desired_capabilities=DesiredCapabilities.CHROME,
        )
    else:
        docker_container_ip = os.getenv("DOCKER_CONTAINER_IP", "127.0.0.1")
        remote_browser_url = "http://{ip}:{port}/wd/hub".format(
            ip=docker_container_ip, port=browser_port
        )
        try:
            return RemoteWebdriver(remote_browser_url, desire_capabilities)
        except (NewConnectionError, MaxRetryError):
            raise DockerNotFoundException(
                "Couldn't connect to remote host for browser.\n "
                "If you use a docker container with an ip different from '127.0.0.1' "
                "you need to expose the ip address via the Environment variable "
                "'DOCKER_CONTAINER_IP'. "
                "Also make sure that the docker images are running (`docker-compose ps`)."
                "If not change to the root directory of 'djangocms-equation' and run "
                "`docker-compose up -d`."
                "See the docs of 'djangocms-equation' for more help."
            )


class ScreenCreator:
    def __init__(self, browser, browser_name="", use_percy=False):
        self.browser = browser
        self.browser_name = browser_name
        self.run_percy = self.is_on_travis(use_percy)
        self.counter = 0

    def is_on_travis(self, use_percy):
        if (
            "TRAVIS" in os.environ
            and use_percy
            # and os.environ.get("TRAVIS_PULL_REQUEST", "false") != "false"
        ):
            self.init_percy()
            return True
        else:
            return False

    def reset_counter(self):
        self.counter = 0

    def take(self, filename, sub_dir="", take_screen_shot=True):
        if take_screen_shot:
            self.counter += 1
            if self.run_percy:
                tox_env = os.getenv("TOX_ENV_NAME", "")
                self.percy_runner.snapshot(
                    name="{} - {} - #{}_{}".format(
                        tox_env, sub_dir, self.counter, filename
                    )
                )
            else:
                filename = "#{}_{}".format(self.counter, filename)
                # this is to prevent visual diffs with percy
                self.insert_css_Rules(
                    ["a{color: black;}"]  # sets the color of links to black
                )
                self.hide_elements(
                    [".cms-messages", "#nprogress"]  # popup messages  # progress bar
                )
                self.browser.save_screenshot(
                    screen_shot_path(filename, self.browser_name, sub_dir)
                )

    def insert_css_Rules(self, css_rules):
        for css_rule in css_rules:
            try:
                script_code = (
                    "document.styleSheets[document.styleSheets.length-1].insertRule("
                    '"{}"'
                    ", document.styleSheets[document.styleSheets.length-1].cssRules.length)"
                    "".format(css_rule)
                )
                self.browser.execute_script(script_code)
            except JavascriptException:
                pass

    def hide_elements(self, css_selectors):
        for css_selector in css_selectors:
            # in case the element doesn't exist
            try:
                script_code = 'document.querySelector("{}").style.display="none"'.format(
                    css_selector
                )
                self.browser.execute_script(script_code)
            except JavascriptException:
                pass

    def init_percy(self):
        # Build a ResourceLoader that knows how to collect assets for this application.
        loader = percy.ResourceLoader(
            # root_dir=settings.STATIC_ROOT,
            root_dir=get_screenshot_test_base_folder(),
            base_url=quote(settings.STATIC_URL),
            webdriver=self.browser,
        )
        percy_config = percy.Config(default_widths=[1200])
        self.percy_runner = percy.Runner(loader=loader, config=percy_config)
        self.percy_runner.initialize_build()

    def stop(self):
        if self.run_percy:
            self.percy_runner.finalize_build()


def get_own_ip():
    """
    returns own ip
    original from:
    https://stackoverflow.com/a/25850698/3990615
    """
    # alternativ use travis env vars
    # SSH_CONNECTION=10.10.16.23 35284 10.20.0.218 22
    # matching regex:
    # ".*?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s+\d+\s(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 1))  # connect() for UDP doesn't send packets
    local_ip_address = s.getsockname()[0]
    return local_ip_address
