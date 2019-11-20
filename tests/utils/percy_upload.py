# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals


from django.test import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.webdriver.support import ui
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from .helper_functions import get_own_ip, get_browser_instance, ScreenCreator

from .generate_screenshot_test_report import (
    get_screenshot_test_base_folder,
    generate_test_screenshot_report,
)


@override_settings(DEBUG=True)
@override_settings(ALLOWED_HOSTS=["*"])
@override_settings(STATIC_URL="/static/")
@override_settings(STATICFILES_DIRS=(get_screenshot_test_base_folder(),))
class PercyScreenshotGenerator(StaticLiveServerTestCase):
    host = get_own_ip()
    browser_port = 4444
    desire_capabilities = DesiredCapabilities.CHROME

    @classmethod
    def setUpClass(cls):
        super(PercyScreenshotGenerator, cls).setUpClass()
        cls.browser = get_browser_instance(cls.browser_port, cls.desire_capabilities)
        cls.screenshot = ScreenCreator(cls.browser, use_percy=True)
        cls.wait = ui.WebDriverWait(cls.browser, 10)

    @classmethod
    def tearDownClass(cls):
        cls.screenshot.stop()
        cls.browser.quit()
        super(PercyScreenshotGenerator, cls).tearDownClass()

    def test_generate_percy_screenshot(self):
        report_filenames = generate_test_screenshot_report(percy_local_develop=True)
        if self.screenshot.is_CI(True):
            for report_filename in report_filenames:
                self.browser.get(
                    "{}/static/{}".format(self.live_server_url, report_filename)
                )
                self.screenshot.take("{}.png".format(report_filename[:-5]))
