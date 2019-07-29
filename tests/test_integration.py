# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
from time import sleep

from cms import __version__ as cms_version

from django.test import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from djangocms_helper.base_test import BaseTransactionTestCase


from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    JavascriptException,
)
from selenium.webdriver.support import ui
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from .utils.helper_functions import (
    get_browser_instance,
    get_own_ip,
    ScreenCreator,
    retry_on_browser_exception,
)

INTERACTIVE = False


# uncomment the next line if the server throws errors
@override_settings(DEBUG=False)
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
    cms_version_tuple = tuple(map(int, cms_version.split(".")))
    browser_port = 4444
    desire_capabilities = DesiredCapabilities.CHROME
    desire_capabilities["unexpectedAlertBehaviour"] = "accept"
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
            cls.browser_port,
            cls.desire_capabilities,
            interactive=INTERACTIVE,
            browser_name=cls.browser_name,
        )
        cls.browser.set_window_size(1100, 1200)
        cls.screenshot = ScreenCreator(cls.browser, cls.browser_name)
        cls.wait = ui.WebDriverWait(cls.browser, 20)
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

    def wait_for_element_to_disapear(self, css_selector):
        try:
            self.browser.find_element_by_css_selector(css_selector)
        except StaleElementReferenceException:
            pass
        else:
            if self.browser.find_element_by_css_selector(css_selector).is_displayed():
                self.wait.until_not(
                    lambda driver: driver.find_element_by_css_selector(
                        css_selector
                    ).is_displayed()
                )

    def wait_for_element_to_be_visable(self, css_selector):
        try:
            self.browser.find_element_by_css_selector(css_selector)
        except StaleElementReferenceException:
            pass
        else:
            if not self.browser.find_element_by_css_selector(
                css_selector
            ).is_displayed():
                self.wait.until(
                    lambda driver: driver.find_element_by_css_selector(
                        css_selector
                    ).is_displayed()
                )

    def set_text_input_value(self, input, value):
        if input.get_attribute("value") == "":
            input.send_keys(value)

    def sleep(self, time=60, allways_sleep=False):
        if (INTERACTIVE and "TRAVIS" not in os.environ) or allways_sleep:
            sleep(time)

    def is_logged_in(self):
        try:
            self.browser.find_element_by_css_selector(".cms-btn-switch-save")
            return True
        except NoSuchElementException:
            return False

    def login_user(self, take_screen_shot=False):
        @retry_on_browser_exception(exceptions=(TimeoutException))
        def enter_edit_mode():
            # check if the user is in edit mode
            if not self.is_logged_in():
                edit_btn = self.wait_get_element_css(".cms-btn-switch-edit")
                edit_btn.click()

        if not self.is_logged_in():
            self.browser.get(self.live_server_url + "/?edit")
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
        enter_edit_mode()

    def logout_user(self):
        # visiting the logout link is a fallback since FireFox
        # sometimes doesn't logout properly by just deleting the coockies
        self.browser.get(self.live_server_url + "/admin/logout/")
        # self.browser.delete_all_cookies()

    @retry_on_browser_exception(exceptions=(ElementNotInteractableException))
    def open_structure_board(
        self, self_test=False, test_name="test_create_standalone_equation"
    ):
        structure_board = self.wait_get_element_css(".cms-structure")
        if not structure_board.is_displayed():
            sidebar_toggle_btn = self.wait_get_element_css(
                ".cms-toolbar-item-cms-mode-switcher a"
            )
            sidebar_toggle_btn.click()

    @retry_on_browser_exception(exceptions=(TimeoutException))
    def enter_equation(
        self,
        self_test=False,
        tex_code=r"\int^{a}_{b} f(x) \mathrm{d}x",
        font_size_value=1,
        font_size_unit="rem",
        is_inline=False,
        test_name="test_create_standalone_equation",
        not_js_injection_hack=True,
    ):
        latex_input = self.wait_get_element_css("#id_tex_code")
        # the click is needed for firefox to select the element
        latex_input.click()
        self.set_text_input_value(latex_input, tex_code)
        if font_size_value != 1 or font_size_unit != "rem" or is_inline is True:
            try:
                self.browser.find_element_by_css_selector(
                    ".collapse.advanced.collapsed"
                )
            except NoSuchElementException:
                pass
            else:
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
            self.sleep(2)
        self.screenshot.take(
            "equation_entered.png", test_name, take_screen_shot=not_js_injection_hack
        )

    @retry_on_browser_exception(
        exceptions=(StaleElementReferenceException, TimeoutException)
    )
    def open_stand_alone_add_modal(
        self,
        self_test=False,
        test_name="test_create_standalone_equation",
        plugin_to_add="equation",
    ):
        add_plugin_btn = self.wait_get_element_css(
            ".cms-submenu-btn.cms-submenu-add.cms-btn"
        )
        add_plugin_btn.click()
        # #### Firefox Hack, since it fails sometimes to open the modal
        self.wait_for_element_to_be_visable(".cms-modal")
        # prevent scroll errors
        quick_search = self.wait_get_element_css(".cms-quicksearch input")
        quick_search.click()
        # since the element sometimes isn't visible the selection is
        # done via with javascript
        self.browser.execute_script(
            'document.querySelector(".cms-quicksearch input").select()'
        )
        if plugin_to_add == "equation":
            # self.set_text_input_value(quick_search, "eq")
            plugin_option = self.wait_get_element_css(
                '.cms-submenu-item a[href="EquationPlugin"]'
            )
        elif plugin_to_add == "text":
            # self.set_text_input_value(quick_search, "text")
            plugin_option = self.wait_get_element_css(
                '.cms-submenu-item a[href="TextPlugin"]'
            )

        self.screenshot.take(
            "plugin_add_modal.png", test_name, take_screen_shot=self_test
        )
        plugin_option.click()

    @retry_on_browser_exception(max_retry=1)
    def hide_structure_mode_cms_34(self):
        if self.cms_version_tuple < (3, 5):
            content_link = self.wait_get_element_css(
                '.cms-toolbar-item-cms-mode-switcher a[href="?edit"]'
            )
            content_link.click()

    def create_standalone_equation(
        self,
        self_test=False,
        tex_code=r"\int^{a}_{b} f(x) \mathrm{d}x",
        font_size_value=1,
        font_size_unit="rem",
        is_inline=False,
        test_name="test_create_standalone_equation",
        not_js_injection_hack=True,
    ):

        self.login_user()
        self.open_structure_board(self_test=self_test, test_name=test_name)
        self.screenshot.take("sidebar_open.png", test_name, take_screen_shot=self_test)

        self.open_stand_alone_add_modal(
            self_test=self_test, test_name=test_name, plugin_to_add="equation"
        )
        equation_edit_iframe = self.wait_get_element_css("iframe")
        self.screenshot.take(
            "equation_edit_iframe.png", test_name, take_screen_shot=self_test
        )
        self.browser.switch_to.frame(equation_edit_iframe)

        self.enter_equation(
            self_test=self_test,
            tex_code=tex_code,
            font_size_value=font_size_value,
            font_size_unit=font_size_unit,
            is_inline=is_inline,
            test_name=test_name,
            not_js_injection_hack=not_js_injection_hack,
        )
        self.browser.switch_to.default_content()
        save_btn = self.wait_get_element_css(".cms-btn.cms-btn-action.default")
        save_btn.click()

        self.wait_for_element_to_disapear(".cms-modal")

        self.hide_structure_mode_cms_34()

        self.wait_get_element_css("span.katex")
        self.screenshot.take(
            "equation_rendered.png", test_name, take_screen_shot=not_js_injection_hack
        )

    def create_text_equation(
        self,
        self_test=False,
        tex_code=r"\int^{a}_{b} f(x) \mathrm{d}x",
        font_size_value=1,
        font_size_unit="rem",
        is_inline=False,
        test_name="test_create_text_equation",
    ):
        def switch_to_text_edit_frame():
            self.browser.switch_to.default_content()
            text_edit_iframe = self.wait_get_element_css("iframe")
            self.browser.switch_to.frame(text_edit_iframe)

        def switch_to_cke_wysiwyg_frame():
            switch_to_text_edit_frame()
            cke_wysiwyg_frame = self.wait_get_element_css("iframe.cke_wysiwyg_frame")
            self.browser.switch_to.frame(cke_wysiwyg_frame)

        @retry_on_browser_exception(exceptions=(TimeoutException), test_name=test_name)
        def add_equation_text_plugin():
            switch_to_text_edit_frame()
            plugin_select = self.wait_get_element_css(".cke_button__cmsplugins")
            self.screenshot.take(
                "text_edit_iframe.png", test_name, take_screen_shot=self_test
            )
            plugin_select.click()
            text_edit_pannel_iframe = self.wait_get_element_css(
                "iframe.cke_panel_frame"
            )
            self.browser.switch_to.frame(text_edit_pannel_iframe)
            equation_option = self.wait_get_element_css(
                '.cke_panel_listItem a[rel="EquationPlugin"]'
            )
            equation_option.click()
            switch_to_text_edit_frame()
            equation_edit_iframe = self.wait_get_element_css(
                "iframe.cke_dialog_ui_html"
            )
            self.browser.switch_to.frame(equation_edit_iframe)

        @retry_on_browser_exception(
            exceptions=(TimeoutException, JavascriptException), test_name=test_name
        )
        def add_text(text=" Some text for testing:", counter=0):
            switch_to_cke_wysiwyg_frame()
            self.wait_get_element_css("body p")
            script_code = 'document.querySelector("body p").innerText=" {} "'.format(
                text
            )
            self.browser.execute_script(script_code)

        @retry_on_browser_exception(exceptions=(TimeoutException), test_name=test_name)
        def save_equation_text_plugin():
            switch_to_text_edit_frame()

            OK_btn = self.wait_get_element_css(".cke_dialog_ui_button_ok")
            OK_btn.click()
            # self.sleep()

            # making sure that equation properly propagated, to the text editor
            switch_to_cke_wysiwyg_frame()
            # self.wait_for_element_to_be_visable("span.katex")
            self.wait_get_element_css("span.katex")

            switch_to_text_edit_frame()
            self.screenshot.take(
                "equation_in_text_editor.png", test_name, take_screen_shot=self_test
            )

            self.browser.switch_to.default_content()
            save_btn = self.wait_get_element_css(".cms-btn.cms-btn-action.default")
            save_btn.click()

        self.login_user()
        self.open_structure_board(self_test=self_test, test_name=test_name)

        self.open_stand_alone_add_modal(
            self_test=self_test, test_name=test_name, plugin_to_add="text"
        )

        add_text()

        add_equation_text_plugin()

        self.enter_equation(
            self_test=self_test,
            tex_code=tex_code,
            font_size_value=font_size_value,
            font_size_unit=font_size_unit,
            is_inline=is_inline,
            test_name=test_name,
            not_js_injection_hack=True,
        )

        save_equation_text_plugin()

        self.browser.switch_to.default_content()
        self.wait_for_element_to_disapear(".cms-modal")

        self.hide_structure_mode_cms_34()

        self.wait_get_element_css("span.katex-html")
        self.screenshot.take("equation_rendered.png", test_name, take_screen_shot=True)

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

    def js_injection_hack(self):
        if self.cms_version_tuple < (3, 7):
            self.create_standalone_equation(
                tex_code="js~injection~hack~for~cms<3.7", not_js_injection_hack=False
            )
            self.browser.refresh()
            # self.delete_plugin(delete_all=True)
            # self.wait_for_element_to_disapear(".cms-messages")
            # self.screenshot.hide_elements([".cms-modal-iframe"])
            # # adding the css back
            # script_code = (
            #     "document.querySelector('head').innerHTML += '"
            #     "<link "
            #     'rel="stylesheet" '
            #     'href="/static/djangocms_equation/css/change_form_template.css" '
            #     'type="text/css"'
            #     "/>'"
            # )
            # self.browser.execute_script(script_code)

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

    def test_create_text_equation(self):
        self.js_injection_hack()
        self.create_text_equation(self_test=True)

    def test_create_text_equation_2rem(self):
        self.js_injection_hack()
        self.create_text_equation(
            font_size_value=2, test_name="test_create_text_equation_2rem"
        )

    def test_create_text_equation_1_in(self):
        self.js_injection_hack()
        self.create_text_equation(
            font_size_unit="in", test_name="test_create_text_equation_1_in"
        )

    def test_create_text_equation_inline_True(self):
        self.js_injection_hack()
        self.create_text_equation(
            is_inline=True, test_name="test_create_text_equation_inline_True"
        )


class TestIntegrationFirefox(TestIntegrationChrome):
    browser_port = 4445
    desire_capabilities = DesiredCapabilities.FIREFOX
    browser_name = "FireFox"
