# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
import re
import socket
from time import sleep

from django.test import override_settings
from djangocms_helper.base_test import BaseTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class DockerNotFoundException(Exception):
    pass


def screen_shot_path(filename):
    tox_env_name = os.getenv("TOX_ENV_NAME", "")
    dir_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "test_screenshots", tox_env_name)
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
        # cls.browser = Chrome(executable_path="D:\inno_Admin_Dropbox\Dropbox\innoAdmin\software_downloader\chromedriver_win32\chromedriver.exe")
        cls.browser.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        # cls.browser.quit()
        super(TestIntegrationChrome, cls).tearDownClass()

    def setUp(self):
        super(TestIntegrationChrome, self).setUp()

    def test_page_loaded(self):
        self.browser.get(self.live_server_url)
        body = self.browser.find_element_by_css_selector("body")

        login_form = body.find_element_by_css_selector("#login-form")
        username = login_form.find_element_by_css_selector("#id_username")
        # username.send_keys(self._staff_user_username)
        username.send_keys(self._admin_user_username)
        password = login_form.find_element_by_css_selector("#id_password")
        # password.send_keys(self._staff_user_password)
        password.send_keys(self._admin_user_password)
        login_form.submit()

        next_btn = self.browser.find_element_by_link_text("Next")
        next_btn.click()


        # for input in body.find_elements_by_css_selector("iframe"):
        #     print(input.get_attribute('outerHTML'))
        #     print(input)

        self.browser.save_screenshot(screen_shot_path("foo.png"))
        self.browser.save_screenshot(screen_shot_path("foo2.png"))
        # sleep(600)
        self.assertNotEquals(body.text, "1")


# class TestIntegrationFirefox(TestIntegrationChrome):
#     browser_remote_address = get_browser_remote_address(4445)
#     desire_capabilities = DesiredCapabilities.FIREFOX
