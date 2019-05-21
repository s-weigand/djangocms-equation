# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
import socket

from django.test import override_settings
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from djangocms_helper.base_test import BaseTestCase

from selenium.webdriver import Chrome
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebdriver
from selenium.webdriver.support import ui
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from urllib3.exceptions import NewConnectionError, MaxRetryError

import percy
from six.moves.urllib.parse import quote

from .generate_test_screenshot_md import get_screenshot_test_base_folder


class DockerNotFoundException(Exception):
    pass


def screen_shot_path(filename, sub_dir=""):
    base_folder = get_screenshot_test_base_folder()
    dir_path = os.path.join(base_folder, sub_dir)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    return os.path.join(dir_path, filename)


def get_browser_instance(browser_port, desire_capabilities, interactive=False):
    if interactive:
        try:
            return Chrome(desired_capabilities=DesiredCapabilities.CHROME)
        except WebDriverException:
            raise WebDriverException(
                "'chromedriver' executable needs to be in PATH. "
                "Please see https://sites.google.com/a/chromium.org/chromedriver/home "
                "or run `pip install chromedriver_installer`."
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
    def __init__(self, browser):
        self.browser = browser
        self.run_percy = self.is_on_travis()
        self.counter = 0

    def is_on_travis(self):
        if (
            "TRAVIS" in os.environ
            and "USE_PERCY" in os.environ
            and os.environ.get("TRAVIS_PULL_REQUEST", "false") != "false"
        ):
            self.init_percy()
            return True
        else:
            return False

    def reset_counter(self):
        self.counter = 0

    def take(self, filename, sub_dir=""):
        self.counter += 1
        if self.run_percy:
            tox_env = os.getenv("TOX_ENV_NAME", "")
            self.percy_runner.snapshot(
                name="{} - {} - #{}_{}".format(tox_env, sub_dir, self.counter, filename)
            )
        else:
            filename = "#{}_{}".format(self.counter, filename)
            self.browser.save_screenshot(screen_shot_path(filename, sub_dir))

    def init_percy(self):
        # Build a ResourceLoader that knows how to collect assets for this application.
        loader = percy.ResourceLoader(
            root_dir=settings.STATIC_ROOT,
            base_url=quote(settings.STATIC_URL),
            webdriver=self.browser,
        )
        self.percy_runner = percy.Runner(loader=loader)
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


# uncomment the next line if the server throws errors
@override_settings(DEBUG=True)
@override_settings(ALLOWED_HOSTS=["*"])
class TestIntegrationChrome(BaseTestCase, StaticLiveServerTestCase):
    """
    Baseclass for Integration tests with Selenium running in a docker.
    The settings default to chrome (see. docker-compose.yml),
    but can be overwritten in subclasses to match different browsers.
    Original setup from:
    https://stackoverflow.com/a/45324730/3990615
    and
    https://docs.djangoproject.com/en/2.2/topics/testing/tools/#liveservertestcase

    """

    host = get_own_ip()  # '192.168.178.20'
    browser_port = 4444
    desire_capabilities = DesiredCapabilities.CHROME

    @classmethod
    def setUpClass(cls):
        super(TestIntegrationChrome, cls).setUpClass()
        cls.browser = get_browser_instance(cls.browser_port, cls.desire_capabilities)
        cls.screenshot = ScreenCreator(cls.browser)
        cls.wait = ui.WebDriverWait(cls.browser, 10)
        cls.create_test_page()

    @classmethod
    def tearDownClass(cls):
        cls.screenshot.stop()
        cls.browser.quit()
        super(TestIntegrationChrome, cls).tearDownClass()

    def setUp(self):
        self.screenshot.reset_counter()
        super(TestIntegrationChrome, self).setUp()

    @classmethod
    def wait_get_element_css(cls, css_selector):
        cls.wait.until(lambda driver: driver.find_element_by_css_selector(css_selector))
        return cls.browser.find_element_by_css_selector(css_selector)

    @classmethod
    def create_test_page(cls):
        cls.browser.get(cls.live_server_url)
        cls.screenshot.take("initial_page.png", "create_test_page")
        login_form = cls.wait_get_element_css("#login-form")

        cls.screenshot.take("login-form_empty.png", "create_test_page")

        username = cls.wait_get_element_css("#id_username")
        username.send_keys(cls._admin_user_username)
        password = cls.wait_get_element_css("#id_password")
        password.send_keys(cls._admin_user_password)

        cls.screenshot.take("login-form_filled_out.png", "create_test_page")
        login_form.submit()

        next_btn = cls.browser.find_element_by_link_text("Next")
        next_btn.click()
        cls.browser.switch_to.frame(cls.wait_get_element_css("iframe"))

        cls.wait_get_element_css("input")

        cls.screenshot.take("create-page-iframe_empty.png", "create_test_page")
        create_page_form = cls.wait_get_element_css("form")
        title_input = create_page_form.find_element_by_css_selector("#id_1-title")
        title_input.send_keys("test_page")
        cls.screenshot.take("create-page-iframe_filled_out.png", "create_test_page")
        create_page_form.submit()
        cls.browser.switch_to.default_content()
        cls.screenshot.take("created_page.png", "create_test_page")

    def test_test_page_created(self):
        self.browser.get(self.live_server_url)
        body = self.browser.find_element_by_css_selector("body")
        self.screenshot.take("created_page2.png", "test_test_page_created")
        self.assertIn("test_page", body.text)


# class TestIntegrationFirefox(TestIntegrationChrome):
#     browser_remote_address = get_browser_remote_address(4445)
#     desire_capabilities = DesiredCapabilities.FIREFOX
