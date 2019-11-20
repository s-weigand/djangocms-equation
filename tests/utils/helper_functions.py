# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import functools
import os
import re
import socket
from time import sleep

from django.conf import settings


from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from urllib3.exceptions import NewConnectionError, MaxRetryError

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    JavascriptException,
)

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

import percy
from six.moves.urllib.parse import quote

from .generate_screenshot_test_report import get_screenshot_test_base_folder


class DockerNotFoundException(Exception):
    pass


class InvalidBrowserNameException(Exception):
    pass


def get_docker_ip():
    docker_host = os.environ.get("DOCKER_HOST", "127.0.0.1")
    docker_ip = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", docker_host)
    return docker_ip.group(1)


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
        options = Options()
        # allows to copy paste in console when in interactive session
        options.preferences.update({"devtools.selfxss.count": 100})
        return Firefox(
            options=options,
            executable_path=GeckoDriverManager().install(),
            desired_capabilities=DesiredCapabilities.FIREFOX,
        )

    elif interactive and "TRAVIS" not in os.environ:
        return Chrome(
            ChromeDriverManager().install(),
            desired_capabilities=DesiredCapabilities.CHROME,
        )
    else:
        docker_container_ip = get_docker_ip()
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
                "'DOCKER_HOST' (normally done by docker itself). "
                "Also make sure that the docker images are running (`docker-compose ps`)."
                "If not change to the root directory of 'djangocms-equation' and run "
                "`docker-compose up -d`."
                "See the docs of 'djangocms-equation' for more help."
            )


def retry_on_browser_exception(
    max_retry=2,
    exceptions=(
        NoSuchElementException,
        TimeoutException,
        ElementNotInteractableException,
        StaleElementReferenceException,
        JavascriptException,
    ),
    test_name="",
    sleep_time_on_exception=0,
    raise_exception=True,
    suppress_report=False,
):
    def outer_wrapper(func):
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            if "test_name" in kwargs:
                func_wrapper.test_name = kwargs["test_name"]
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                # used for interactive testing
                if func_wrapper.sleep_time_on_exception != 0:
                    sleep(sleep_time_on_exception)
                if func_wrapper.counter <= max_retry:

                    error_information = "In function: `{}`, args:{}, kwargs: {}`".format(
                        func.__name__, args, kwargs
                    )
                    if func_wrapper.test_name != "":
                        error_information += ", run by the test: {}".format(
                            func_wrapper.test_name
                        )
                    if not func_wrapper.suppress_report:
                        print()
                        print(type(e).__name__, ": ")
                        print(error_information)
                        print(e)
                    func_wrapper.counter += 1
                    return func_wrapper(*args, **kwargs)
                else:
                    if raise_exception:
                        raise e

        func_wrapper.counter = 0
        func_wrapper.test_name = test_name
        func_wrapper.sleep_time_on_exception = sleep_time_on_exception
        func_wrapper.suppress_report = suppress_report
        return func_wrapper

    return outer_wrapper


@retry_on_browser_exception(
    exceptions=(JavascriptException,), raise_exception=False, suppress_report=True
)
def insert_css_Rules(browser, css_rules):
    exception_counter = 0
    for css_rule in css_rules:
        try:
            script_code = (
                "document.styleSheets[document.styleSheets.length-1].insertRule("
                '"{}"'
                ", document.styleSheets[document.styleSheets.length-1].cssRules.length)"
                "".format(css_rule)
            )
            browser.execute_script(script_code)
        except JavascriptException:
            exception_counter += 1
    if exception_counter:
        raise JavascriptException("exception, found in insert_css_Rules")


@retry_on_browser_exception(
    exceptions=(JavascriptException,), raise_exception=False, suppress_report=True
)
def hide_elements(browser, css_selectors):
    exception_counter = 0
    for css_selector in css_selectors:
        try:
            script_code = 'document.querySelector("{}").style.display="none"'.format(
                css_selector
            )
            browser.execute_script(script_code)
        except JavascriptException:
            exception_counter += 1
    if exception_counter:
        raise JavascriptException("exception, found in hide_elements")


def normalize_screenshot(browser):
    insert_css_Rules(
        browser,
        [
            "a{color: black;}",  # sets the color of links to black
            "div.cms .cms-form-login input[type=password]:focus, "  # removes outline on focus
            "div.cms .cms-form-login input[type=text]:focus"
            "{border: 1px solid #d9d9d9;"
            "box-shadow: 0 1px 0 #fff;"
            "outline: none;}",
        ],
    )
    hide_elements(
        browser, [".cms-messages", "#nprogress"]  # popup messages  # progress bar
    )


class ScreenCreator:
    def __init__(self, browser, browser_name="", use_percy=False):
        self.browser = browser
        self.browser_name = browser_name
        self.run_percy = self.is_CI(use_percy)
        self.counter = 0

    def is_CI(self, use_percy):
        if use_percy and os.environ.get("GITHUB_REF", "").lower().endswith("master"):
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
                normalize_screenshot(self.browser)
                self.browser.save_screenshot(
                    screen_shot_path(filename, self.browser_name, sub_dir)
                )

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


def get_page_placeholders(page, language=None):
    try:
        # cms3.6 compat
        return page.get_placeholders()
    except TypeError:
        return page.get_placeholders(language)


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
