# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
import re
import socket

from django.test import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from djangocms_helper.base_test import BaseTestCase

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import ui
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class DockerNotFoundException(Exception):
    pass


def screen_shot_path(filename, sub_dir=""):
    tox_env_name = os.getenv("TOX_ENV_NAME", "")
    dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "test_screenshots", tox_env_name, sub_dir
        )
    )
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    return os.path.join(dir_path, filename)


def get_docker_container_ip():
    """
    Using 'DOCKER_HOST' is a workaround for Windows with 'Docker Toolbox'
    (I don't want hyper-V if I can't use my trusty old VirtualBox).

    """
    docker_host = os.getenv("DOCKER_HOST", "")
    docker_ip_travis = os.getenv("DOCKER_IP_TRAVIS")
    ip_match = re.match(
        r".*?\/\/(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", docker_host
    )
    if ip_match:
        return ip_match.group("ip")
    elif docker_ip_travis:
        return docker_ip_travis
    else:
        raise DockerNotFoundException(
            "The environment variable 'DOCKER_HOST' was not found!"
            "On Windows running the tests as admin might help."
        )


def get_browser_remote_address(docker_port):
    """[summary]

    Parameters
    ----------
    docker_port : int
        [description]
    """
    docker_container_ip = get_docker_container_ip()
    return "http://{ip}:{port}/wd/hub".format(ip=docker_container_ip, port=docker_port)


def get_own_ip():
    """
    returns own ip
    """
    return socket.gethostbyname(socket.gethostname())


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
    browser_remote_address = get_browser_remote_address(4444)
    desire_capabilities = DesiredCapabilities.CHROME

    @classmethod
    def setUpClass(cls):
        super(TestIntegrationChrome, cls).setUpClass()
        cls.browser = WebDriver(cls.browser_remote_address, cls.desire_capabilities)
        cls.wait = ui.WebDriverWait(cls.browser, 10)
        cls.create_test_page()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(TestIntegrationChrome, cls).tearDownClass()

    def setUp(self):
        super(TestIntegrationChrome, self).setUp()

    @classmethod
    def wait_get_element_css(cls, css_selector):
        cls.wait.until(lambda driver: driver.find_element_by_css_selector(css_selector))
        return cls.browser.find_element_by_css_selector(css_selector)

    @classmethod
    def create_test_page(cls):
        cls.browser.get(cls.live_server_url)
        login_form = cls.wait_get_element_css("#login-form")
        cls.browser.save_screenshot(
            screen_shot_path("#1_login-form_empty.png", "create_test_page")
        )

        username = cls.wait_get_element_css("#id_username")
        username.send_keys(cls._admin_user_username)
        password = cls.wait_get_element_css("#id_password")
        password.send_keys(cls._admin_user_password)
        cls.browser.save_screenshot(
            screen_shot_path("#2_login-form_filled_out.png", "create_test_page")
        )
        login_form.submit()

        next_btn = cls.browser.find_element_by_link_text("Next")
        next_btn.click()
        cls.browser.switch_to.frame(cls.wait_get_element_css("iframe"))

        cls.wait_get_element_css("input")

        # for input in self.browser.find_elements_by_css_selector("form"):
        #     print(input.get_attribute("outerHTML"))
        #     print(input)
        cls.browser.save_screenshot(
            screen_shot_path("#3_create-page-iframe_empty.png", "create_test_page")
        )
        create_page_form = cls.wait_get_element_css("form")
        title_input = create_page_form.find_element_by_css_selector("#id_1-title")
        title_input.send_keys("test_page")
        cls.browser.save_screenshot(
            screen_shot_path("#4_create-page-iframe_filled_out.png", "create_test_page")
        )
        create_page_form.submit()
        cls.browser.switch_to.default_content()

        cls.browser.save_screenshot(
            screen_shot_path("#5_created_page.png", "create_test_page")
        )

    def test_test_page_created(self):
        self.browser.get(self.live_server_url)
        body = self.browser.find_element_by_css_selector("body")
        self.browser.save_screenshot(screen_shot_path("page_created2.png"))
        self.assertIn("test_page", body.text)


# class TestIntegrationFirefox(TestIntegrationChrome):
#     browser_remote_address = get_browser_remote_address(4445)
#     desire_capabilities = DesiredCapabilities.FIREFOX
