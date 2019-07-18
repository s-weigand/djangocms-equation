# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
from time import sleep

from cms import __version__ as cms_version

from django.test import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from djangocms_helper.base_test import BaseTransactionTestCase

from selenium.webdriver.support import ui
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from .utils.helper_functions import get_browser_instance, get_own_ip, ScreenCreator

INTERACTIVE = False


# uncomment the next line if the server throws errors
@override_settings(DEBUG=True)
@override_settings(ALLOWED_HOSTS=["*"])
class TestIntegrationChrome(BaseTransactionTestCase, StaticLiveServerTestCase):
    """
    Baseclass for Integration tests with Selenium running in a docker.
    The settings default to chrome (see. docker-compose.yml),
    but can be overwritten in subclasses to match different browsers.
    Original setup from:
    https://stackoverflow.com/a/45324730/3990615
    and
    https://docs.djangoproject.com/en/2.2/topics/testing/tools/#liveservertestcase

    """

    host = get_own_ip()
    browser_port = 4444
    desire_capabilities = DesiredCapabilities.CHROME
    browser_name = "Chrome"
    _pages_data = (
        {
            "en": {
                "title": "testpage",
                "template": "page.html",
                "publish": True,
                "menu_title": "test_page",
                "in_navigation": True,
            }
        },
    )
    languages = ["en"]

    @classmethod
    def setUpClass(cls):
        cls.browser = get_browser_instance(
            cls.browser_port, cls.desire_capabilities, interactive=INTERACTIVE
        )
        cls.browser.set_window_size(1366, 768)
        cls.screenshot = ScreenCreator(cls.browser, cls.browser_name)
        cls.wait = ui.WebDriverWait(cls.browser, 10)
        cls.browser.delete_all_cookies()

    @classmethod
    def tearDownClass(cls):
        cls.screenshot.stop()
        cls.browser.quit()
        super(TestIntegrationChrome, cls).tearDownClass()

    def setUp(self):
        # This is needed so the users will be recreated each time,
        # since TransactionTestCase drops its db per test
        super(TestIntegrationChrome, self).setUpClass()
        self.get_pages()
        self.logout_user()
        self.screenshot.reset_counter()
        super(TestIntegrationChrome, self).setUp()

    @classmethod
    def wait_get_element_css(cls, css_selector):
        cls.wait.until(lambda driver: driver.find_element_by_css_selector(css_selector))
        return cls.browser.find_element_by_css_selector(css_selector)

    @classmethod
    def wait_get_elements_css(cls, css_selector):
        cls.wait.until(
            lambda driver: driver.find_elements_by_css_selector(css_selector)
        )
        return cls.browser.find_elements_by_css_selector(css_selector)

    @classmethod
    def wait_get_element_link_text(cls, link_text):
        cls.wait.until(lambda driver: driver.find_element_by_link_text(link_text))
        return cls.browser.find_element_by_link_text(link_text)

    def sleep(self):
        if INTERACTIVE and "TRAVIS" not in os.environ:
            sleep(60)

    def is_logged_in(self):
        try:
            self.browser.find_element_by_css_selector(
                ".cms-toolbar-item-navigation span"
            )
            return True
        except NoSuchElementException:
            return False

    def login_user(self, take_screen_shot=False):
        if not self.is_logged_in():
            self.browser.get(self.live_server_url + "/?edit")
        if not self.is_logged_in():
            try:
                username = self.wait_get_element_css("#id_username")
                username.send_keys(self._admin_user_username)
                password = self.wait_get_element_css("#id_password")
                password.send_keys(self._admin_user_password)
                self.screenshot.take(
                    "added_credentials.png",
                    "test_login_user",
                    take_screen_shot=take_screen_shot,
                )
                login_form = self.wait_get_element_css("form.cms-form-login")
                login_form.submit()
                self.screenshot.take(
                    "form_submitted.png",
                    "test_login_user",
                    take_screen_shot=take_screen_shot,
                )
            except TimeoutException as e:
                print("Didn't find `form.cms-form-login`.")
                self.screenshot.take("login_fail.png", "login_fail")
                raise TimeoutException(e.msg)

    def logout_user(self):
        # visiting the logout link is a fallback since FireFox
        # sometimes doesn't logout properly by just deleting the coockies
        self.browser.get(self.live_server_url + "/admin/logout/")
        self.browser.delete_all_cookies()

    def open_structure_board(self):
        structure_board = self.wait_get_element_css(".cms-structure")
        if not structure_board.is_displayed():
            sidebar_toggle_btn = self.wait_get_element_css(
                ".cms-toolbar-item-cms-mode-switcher a"
            )
            sidebar_toggle_btn.click()

    def enter_equation(
        self,
        self_test=False,
        tex_code=r"\int^{a}_{b} f(x) \mathrm{d}x",
        font_size_value=1,
        font_size_unit="rem",
        is_inline=False,
        test_name="test_create_standalone_equation",
    ):
        equation_edit_iframe = self.wait_get_element_css("iframe")
        self.screenshot.take(
            "equation_edit_iframe.png", test_name, take_screen_shot=self_test
        )
        self.browser.switch_to.frame(equation_edit_iframe)
        latex_input = self.wait_get_element_css("#id_tex_code")
        # the click is needed for firefox to create
        latex_input.click()
        latex_input.send_keys(tex_code)
        if font_size_value != 1 or font_size_unit != "rem" or is_inline is True:
            advanced_setting_toggle = self.wait_get_element_css(".collapse-toggle")
            advanced_setting_toggle.click()

            if font_size_value != 1:
                font_size_value_input = self.wait_get_element_css(
                    "#djangocms_equation_font_size_value"
                )
                font_size_value_input.clear()
                font_size_value_input.send_keys(str(font_size_value))

            if font_size_unit != "rem":
                font_size_unit_input = self.wait_get_element_css(
                    "#djangocms_equation_font_size_unit"
                )
                font_size_unit_input.click()
                unit_option = self.wait_get_element_css(
                    "#djangocms_equation_font_size_unit option[value={}]".format(
                        font_size_unit
                    )
                )
                unit_option.click()

            if is_inline is True:
                is_inline_input = self.wait_get_element_css("#id_is_inline")
                is_inline_input.click()
            self.sleep()
        self.screenshot.take("equation_entered.png", test_name, take_screen_shot=True)

        self.browser.switch_to.default_content()

    def create_standalone_equation(
        self,
        self_test=False,
        tex_code=r"\int^{a}_{b} f(x) \mathrm{d}x",
        font_size_value=1,
        font_size_unit="rem",
        is_inline=False,
        test_name="test_create_standalone_equation",
    ):

        self.login_user()
        self.open_structure_board()
        add_plugin_btn = self.wait_get_element_css(
            ".cms-submenu-btn.cms-submenu-add.cms-btn"
        )
        self.screenshot.take("sidebar_open.png", test_name, take_screen_shot=self_test)
        add_plugin_btn.click()
        # ##### Firefox Hack, to prevent scroll errors
        quick_search = self.wait_get_element_css(".cms-quicksearch input")
        quick_search.click()
        quick_search.send_keys("eq")
        # ######
        equatuion_btn = self.wait_get_element_css(
            '.cms-submenu-item a[href="EquationPlugin"]'
        )
        self.screenshot.take(
            "plugin_add_modal.png", test_name, take_screen_shot=self_test
        )
        equatuion_btn.click()

        self.enter_equation(
            self_test=self_test,
            tex_code=tex_code,
            font_size_value=font_size_value,
            font_size_unit=font_size_unit,
            is_inline=is_inline,
            test_name=test_name,
        )
        save_btn = self.wait_get_element_css(".cms-btn.cms-btn-action.default")

        save_btn.click()

        self.wait_for_element_to_disapear(".cms-modal")

        self.wait_get_element_css("span.katex")
        self.screenshot.take("equation_rendered.png", test_name, take_screen_shot=True)

    def wait_for_element_to_disapear(self, css_selector):
        self.wait.until_not(
            lambda driver: driver.find_element_by_css_selector(
                css_selector
            ).is_displayed()
        )

    def delete_plugin(self, delete_all=True):
        self.open_structure_board()
        delete_links = self.wait_get_elements_css("a[data-rel=delete]")
        if not delete_all:
            delete_links = [delete_links[0]]
        for _ in delete_links:
            # since the delete links aren't visible the click is triggered
            # with javascript
            self.browser.execute_script(
                'document.querySelector("a[data-rel=delete]").click()'
            )
            delete_confirm = self.wait_get_element_css(".deletelink")
            delete_confirm.click()
        self.wait_for_element_to_disapear(".cms-messages")

    def js_injection_hack(self):
        cms_version_tuple = tuple(map(int, cms_version.split(".")))
        if cms_version_tuple < (3, 7):
            self.create_standalone_equation()
            self.browser.refresh()
            self.delete_plugin(delete_all=True)

    def test_page_exists(self):
        self.browser.get(self.live_server_url)
        body = self.browser.find_element_by_css_selector("body")
        self.screenshot.take("created_page.png", "test_page_exists")
        self.assertIn("test_page", body.text)

    def test_login_user(self):
        self.login_user(take_screen_shot=True)
        self.browser.get(self.live_server_url + "/?edit")
        self.screenshot.take("start_page_user_loged_in.png", "test_login_user")
        cms_navigation = self.wait_get_element_css(".cms-toolbar-item-navigation span")
        self.assertEquals(
            cms_navigation.text,
            "example.com",
            cms_navigation.get_attribute("innerHTML"),
        )

    def test_logout_user(self):
        self.login_user()
        self.logout_user()
        self.browser.get(self.live_server_url)
        self.screenshot.take("start_page_user_loged_out.png", "test_logout_user")
        self.assertRaises(
            NoSuchElementException,
            self.browser.find_element_by_css_selector,
            "#cms-top",
        )

    def test_create_standalone_equation(self):
        self.js_injection_hack()
        self.create_standalone_equation(True)

    def test_create_standalone_equation_2rem(self):
        self.js_injection_hack()
        self.create_standalone_equation(
            font_size_value=2, test_name="test_create_standalone_equation_2rem"
        )

    def test_create_standalone_equation_1_in(self):
        self.js_injection_hack()
        self.create_standalone_equation(
            font_size_unit="in", test_name="test_create_standalone_equation_1_in"
        )

    def test_create_standalone_equation_inline_True(self):
        self.js_injection_hack()
        self.create_standalone_equation(
            is_inline=True, test_name="test_create_standalone_equation_inline_True"
        )


if not INTERACTIVE or "TRAVIS" in os.environ:

    class TestIntegrationFirefox(TestIntegrationChrome):
        browser_port = 4445
        desire_capabilities = DesiredCapabilities.FIREFOX
        browser_name = "FireFox"
