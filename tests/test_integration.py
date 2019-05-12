# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
import re
import socket

from django.test import override_settings
from djangocms_helper.base_test import BaseTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class DockerNotFoundException(Exception):
    pass


def screen_shot_path(filename):
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "screenshots", filename)
    )


def get_docker_container_ip():
    """

    """
    docker_host = os.getenv("DOCKER_HOST", "")
    ip_match = re.match(
        r".*?\/\/(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", docker_host
    )
    if ip_match:
        return ip_match.group("ip")
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
        cls.browser.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(TestIntegrationChrome, cls).tearDownClass()

    def setUp(self):
        super(TestIntegrationChrome, self).setUp()

    def test_page_loaded(self):
        self.browser.get(self.live_server_url)
        self.browser.save_screenshot(screen_shot_path("foo.png"))
        # self.assertEquals(self.live_server_url, "")
        body = self.browser.find_element_by_css_selector("body")
        # self.browser.response()
        # print(self.browser.page_source)
        with open(screen_shot_path("foo.html"), "a") as source:
            source.write(self.browser.page_source)
        self.assertNotEquals(body.text, "")


# class TestIntegrationFirefox(TestIntegrationChrome):
#     browser_remote_address = get_browser_remote_address(4445)
#     desire_capabilities = DesiredCapabilities.FIREFOX
