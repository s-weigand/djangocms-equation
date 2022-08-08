import os
from time import sleep

import django
from app_helper.base_test import BaseTestCaseMixin
from cms import __version__ as cms_version
from cms.api import add_plugin
from cms.api import create_page
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.servers.basehttp import WSGIServer
from django.test import override_settings
from django.test.testcases import LiveServerThread
from django.test.testcases import QuietWSGIRequestHandler
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import JavascriptException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import ui

from .utils.helper_functions import ScreenCreator
from .utils.helper_functions import get_browser_instance
from .utils.helper_functions import get_own_ip
from .utils.helper_functions import get_page_placeholders
from .utils.helper_functions import normalize_screenshot
from .utils.helper_functions import retry_on_browser_exception

INTERACTIVE = False

CMS_VERSION_TUPLE = tuple(map(int, cms_version.split(".")))
PATCHED_CMS_VERSION_TUPLE = (3, 8)
if CMS_VERSION_TUPLE < PATCHED_CMS_VERSION_TUPLE:
    USE_JS_INJECTION = True
else:
    USE_JS_INJECTION = False


class LiveServerSingleThread(LiveServerThread):
    """
    From: https://stackoverflow.com/a/51750516/3990615

    Runs a single threaded server rather than multi threaded.
    Reverts https://github.com/django/django/pull/7832
    """

    def _create_server(self):

        """
        the keep-alive fixes introduced in Django 2.1.4 (934acf1126995f6e6ccba5947ec8f7561633c27f)
        cause problems when serving the static files in a stream.
        We disable the helper handle method that calls handle_one_request multiple times.
        """
        QuietWSGIRequestHandler.handle = QuietWSGIRequestHandler.handle_one_request

        return WSGIServer(
            (self.host, self.port), QuietWSGIRequestHandler, allow_reuse_address=False
        )


DJANGO_VERSION_TUPLE = tuple(int(i) for i in django.__version__.split("."))

if DJANGO_VERSION_TUPLE >= (2, 1, 4):

    class StaticServerSingleThreadedTestCase(StaticLiveServerTestCase):
        "A thin sub-class which only sets the single-threaded server as a class"
        server_thread_class = LiveServerSingleThread

else:
    StaticServerSingleThreadedTestCase = StaticLiveServerTestCase


# uncomment the next line if the server throws errors
# @override_settings(DEBUG=True)
@override_settings(ALLOWED_HOSTS=["*"])
class TestIntegrationChrome(BaseTestCaseMixin, StaticServerSingleThreadedTestCase):
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
        super().setUpClass()
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
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        # This is needed so the user will be recreated each time,
        # since TransactionTestCase (base class of StaticLiveServerTestCase)
        # drops its db per test
        self.user = self.create_user(
            self._admin_user_username,
            self._admin_user_email,
            self._admin_user_password,
            is_staff=True,
            is_superuser=True,
        )
        testpage = create_page(
            "testpage",
            "page.html",
            "en",
            menu_title="test_page",
            in_navigation=True,
            published=True,
        )
        if CMS_VERSION_TUPLE >= (3, 5):
            testpage.set_as_homepage()
        self.placeholder = get_page_placeholders(testpage, "en").get(slot="content")
        self.logout_user()
        self.screenshot.reset_counter()
        super().setUp()

    @classmethod
    def wait_get_element_css(cls, css_selector):
        cls.wait.until(lambda driver: driver.find_element_by_css_selector(css_selector))
        return cls.browser.find_element_by_css_selector(css_selector)

    @classmethod
    def wait_get_elements_css(cls, css_selector):
        cls.wait.until(lambda driver: driver.find_elements_by_css_selector(css_selector))
        return cls.browser.find_elements_by_css_selector(css_selector)

    @classmethod
    def wait_get_element_link_text(cls, link_text):
        cls.wait.until(lambda driver: driver.find_element_by_link_text(link_text))
        return cls.browser.find_element_by_link_text(link_text)

    def element_is_displayed_css(self, css_selector):
        if self.element_exists(css_selector):
            try:
                return self.browser.find_element_by_css_selector(css_selector).is_displayed()
            except (
                ElementNotInteractableException,
                StaleElementReferenceException,
                NoSuchElementException,
            ):
                return False
        else:
            return False

    @retry_on_browser_exception(
        max_retry=1,
        exceptions=(
            StaleElementReferenceException,
            NoSuchElementException,
            TimeoutException,
        ),
        raise_exception=False,
    )
    def wait_for_element_to_disappear(self, css_selector):
        try:
            self.browser.find_element_by_css_selector(css_selector)
        except (StaleElementReferenceException, NoSuchElementException):
            pass
        else:
            if self.browser.find_element_by_css_selector(css_selector).is_displayed():
                self.wait.until_not(
                    lambda driver: driver.find_element_by_css_selector(css_selector).is_displayed()
                )

    @retry_on_browser_exception(
        max_retry=1, exceptions=(StaleElementReferenceException, NoSuchElementException)
    )
    def wait_for_element_to_be_visible(self, css_selector):
        try:
            self.browser.find_element_by_css_selector(css_selector)
        except StaleElementReferenceException:
            pass
        else:
            if not self.browser.find_element_by_css_selector(css_selector).is_displayed():
                self.wait.until(
                    lambda driver: driver.find_element_by_css_selector(css_selector).is_displayed()
                )

    def set_text_input_value(self, input, value):
        if input.get_attribute("value") == "":
            input.send_keys(value)

    def sleep(self, time=60, allways_sleep=False):
        if (INTERACTIVE and "GITHUB_WORKSPACE" not in os.environ) or allways_sleep:
            sleep(time)

    def element_exists(self, css_selector):
        try:
            self.browser.find_element_by_css_selector(css_selector)
            return True
        except NoSuchElementException:
            return False

    def login_user(self, take_screen_shot=False):
        if not self.element_exists(".cms-btn-switch-save"):
            self.browser.get(self.live_server_url + "/?edit")
            try:
                username = self.wait_get_element_css("#id_username")
                username.send_keys(self._admin_user_username)  # admin
                password = self.wait_get_element_css("#id_password")
                password.send_keys(self._admin_user_password)  # admin
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

        # make sure that the css for proper screenshots is applied
        normalize_screenshot(browser=self.browser)

    def logout_user(self):
        # visiting the logout link is a fallback since FireFox
        # sometimes doesn't logout properly by just deleting the cookies
        self.browser.get(self.live_server_url + "/admin/logout/")
        # self.browser.delete_all_cookies()

    @retry_on_browser_exception(
        exceptions=(ElementNotInteractableException, StaleElementReferenceException)
    )
    def open_structure_board(
        self,
        self_test=False,
        test_name="test_create_standalone_equation",
        execution_count=0,
    ):
        if execution_count >= 2:
            self.browser.refresh()
        if CMS_VERSION_TUPLE < (3, 5):
            if not self.element_is_displayed_css(".cms-toolbar"):
                # cms_toolbar_btn only exists in django-cms 3.4
                self.click_element_css(".cms-toolbar-trigger a")
        if self.element_is_displayed_css("a.cms-btn-switch-edit"):
            self.click_element_css("a.cms-btn-switch-edit")

        if not self.element_is_displayed_css(".cms-structure"):
            # sidebar_toggle_btn
            self.click_element_css(".cms-toolbar-item-cms-mode-switcher a")
        # This is needed so structure_board won't be stale
        if not self.element_is_displayed_css(".cms-structure"):
            if self.element_is_displayed_css("a.cms-btn-switch-edit"):
                self.click_element_css("a.cms-btn-switch-edit")
            self.open_structure_board(
                self_test=self_test,
                test_name=test_name,
                execution_count=execution_count + 1,
            )

    def change_form_orientation(self, test_name="test_equation_orientation", current_frames=None):
        orientation_changer = self.wait_get_element_css(".orientation_selector")
        orientation_changer.click()
        self.screenshot.take(
            "horizontal_orientation.png",
            test_name,
            take_screen_shot=True,
            current_frames=current_frames,
        )
        orientation_changer.click()
        self.screenshot.take(
            "vertical_orientation.png",
            test_name,
            take_screen_shot=True,
            current_frames=current_frames,
        )
        orientation_changer.click()
        self.screenshot.take(
            "default_orientation_auto_again.png",
            test_name,
            take_screen_shot=True,
            current_frames=current_frames,
        )

    @retry_on_browser_exception(exceptions=(TimeoutException, ElementNotInteractableException))
    def enter_equation(
        self,
        self_test=False,
        tex_code=r"\int^{a}_{b} f(x) \mathrm{d}x",
        font_size_value=1,
        font_size_unit="rem",
        is_inline=False,
        test_name="test_create_standalone_equation",
        not_js_injection_hack=True,
        test_orientation=False,
        current_frames=None,
    ):
        # this is to prevent random errors, when
        # chrome does not manage to click #id_tex_code
        if current_frames is not None:
            self.browser.switch_to.default_content()
            for current_frame in current_frames:
                self.browser.switch_to.frame(current_frame)
        # the click is needed for firefox to select the frame again
        latex_input = self.click_element_css("#id_tex_code")
        if font_size_value != 1 or font_size_unit != "rem" or is_inline is True:
            try:
                self.browser.find_element_by_css_selector(".collapse.advanced.collapsed")
            except NoSuchElementException:
                pass
            else:
                # advanced_setting_toggle
                self.click_element_css(".collapse-toggle")

            if font_size_value != 1:
                font_size_value_input = self.wait_get_element_css(
                    "#djangocms_equation_font_size_value"
                )
                font_size_value_input.clear()
                font_size_value_input.send_keys(str(font_size_value))

            if font_size_unit != "rem":
                # font_size_unit_input
                self.click_element_css("#djangocms_equation_font_size_unit")
                # unit_option
                self.click_element_css(
                    "#djangocms_equation_font_size_unit option[value={}]".format(font_size_unit)
                )

            if is_inline is True:
                # is_inline_input
                self.click_element_css("#id_is_inline")
        # the click is needed for firefox to select the element
        latex_input = self.click_element_css("#id_tex_code")
        # the input of the equation is done here so the browsers
        # have more time to render the settings, since this appears
        # to be a problem on travis
        self.set_text_input_value(latex_input, tex_code)

        self.screenshot.take(
            "equation_entered.png",
            test_name,
            take_screen_shot=not_js_injection_hack,
            current_frames=current_frames,
        )
        if test_orientation:
            self.change_form_orientation(test_name=test_name, current_frames=current_frames)

    @retry_on_browser_exception(exceptions=(StaleElementReferenceException, TimeoutException))
    def open_stand_alone_add_modal(
        self,
        self_test=False,
        test_name="test_create_standalone_equation",
        plugin_to_add="equation",
    ):
        # add_plugin_btn
        self.click_element_css(".cms-submenu-btn.cms-submenu-add.cms-btn")
        # #### Firefox Hack, since it fails sometimes to open the modal
        self.wait_for_element_to_be_visible(".cms-modal")
        # prevent scroll errors
        # quick_search
        self.click_element_css(".cms-quicksearch input")
        if plugin_to_add == "equation":
            plugin_option = self.wait_get_element_css('.cms-submenu-item a[href="EquationPlugin"]')
        elif plugin_to_add == "text":
            plugin_option = self.wait_get_element_css('.cms-submenu-item a[href="TextPlugin"]')

        self.screenshot.take("plugin_add_modal.png", test_name, take_screen_shot=self_test)
        plugin_option.click()

    @retry_on_browser_exception(max_retry=1)
    def hide_structure_mode_cms_34(self):
        if CMS_VERSION_TUPLE < (3, 5):
            # content_link
            self.click_element_css('.cms-toolbar-item-cms-mode-switcher a[href="?edit"]')

    @retry_on_browser_exception(
        max_retry=2,
        exceptions=(
            StaleElementReferenceException,
            TimeoutException,
            NoSuchElementException,
            ElementNotInteractableException,
            ElementClickInterceptedException,
        ),
    )
    def click_element_css(self, css_selector):
        element = self.wait_get_element_css(css_selector)
        element.click()
        return element

    @retry_on_browser_exception(
        max_retry=1, exceptions=(ElementNotInteractableException, TimeoutException)
    )
    def publish_and_take_screen_shot(self, not_js_injection_hack, test_name):
        if not_js_injection_hack:
            if self.element_exists(".cms-btn-publish-active"):
                self.click_element_css(".cms-btn-publish-active")
            # making sure the page got updated
            self.wait_get_element_css("a.cms-btn-switch-edit")
            if not self.element_exists(".cms-btn-publish-active"):
                self.logout_user()
                self.wait_get_element_css(".djangocms-admin-style")
                self.browser.get(self.live_server_url)
                self.wait_get_element_css("span.katex-html")
                self.screenshot.take(
                    "equation_rendered_no_edit_mode.png",
                    test_name,
                    take_screen_shot=True,
                )
            else:
                self.browser.refresh()
                raise ElementNotInteractableException("Couldn't publish page")

    def create_standalone_equation(
        self,
        self_test=False,
        tex_code=r"\int^{a}_{b} f(x) \mathrm{d}x",
        font_size_value=1,
        font_size_unit="rem",
        is_inline=False,
        test_name="test_create_standalone_equation",
        not_js_injection_hack=True,
        test_orientation=False,
    ):

        self.login_user()
        self.open_structure_board(self_test=self_test, test_name=test_name)
        self.screenshot.take("sidebar_open.png", test_name, take_screen_shot=self_test)

        self.open_stand_alone_add_modal(
            self_test=self_test, test_name=test_name, plugin_to_add="equation"
        )
        equation_edit_iframe = self.wait_get_element_css("iframe")
        self.screenshot.take("equation_edit_iframe.png", test_name, take_screen_shot=self_test)
        self.browser.switch_to.frame(equation_edit_iframe)

        self.enter_equation(
            self_test=self_test,
            tex_code=tex_code,
            font_size_value=font_size_value,
            font_size_unit=font_size_unit,
            is_inline=is_inline,
            test_name=test_name,
            not_js_injection_hack=not_js_injection_hack,
            test_orientation=test_orientation,
            current_frames=(equation_edit_iframe,),
        )
        self.browser.switch_to.default_content()

        # save_btn
        self.click_element_css(".cms-btn.cms-btn-action.default")
        if self.element_is_displayed_css(".cms-modal"):
            self.wait_for_element_to_disappear(".cms-modal")

        self.hide_structure_mode_cms_34()
        # self.wait_get_element_css("span.katex")
        if not test_orientation:
            self.screenshot.take(
                "equation_rendered.png",
                test_name,
                take_screen_shot=not_js_injection_hack,
            )
            self.publish_and_take_screen_shot(not_js_injection_hack, test_name)

    def create_text_equation(
        self,
        self_test=False,
        tex_code=r"\int^{a}_{b} f(x) \mathrm{d}x",
        font_size_value=1,
        font_size_unit="rem",
        is_inline=False,
        test_name="test_create_text_equation",
        test_orientation=False,
    ):
        def switch_to_text_edit_frame():
            self.browser.switch_to.default_content()
            text_edit_iframe = self.wait_get_element_css("iframe")
            self.browser.switch_to.frame(text_edit_iframe)
            return text_edit_iframe

        def switch_to_cke_wysiwyg_frame():
            switch_to_text_edit_frame()
            cke_wysiwyg_frame = self.wait_get_element_css("iframe.cke_wysiwyg_frame")
            self.browser.switch_to.frame(cke_wysiwyg_frame)
            return cke_wysiwyg_frame

        @retry_on_browser_exception(exceptions=(TimeoutException), test_name=test_name)
        def add_equation_text_plugin():
            text_edit_frame = switch_to_text_edit_frame()
            plugin_select = self.wait_get_element_css(".cke_button__cmsplugins")
            self.screenshot.take(
                "text_edit_iframe.png",
                test_name,
                take_screen_shot=self_test,
                current_frames=(text_edit_frame,),
            )
            plugin_select.click()
            text_edit_pannel_iframe = self.wait_get_element_css("iframe.cke_panel_frame")
            self.browser.switch_to.frame(text_edit_pannel_iframe)

            # equation_options
            self.click_element_css('.cke_panel_listItem a[rel="EquationPlugin"]')
            text_edit_frame = switch_to_text_edit_frame()
            equation_edit_iframe = self.wait_get_element_css("iframe.cke_dialog_ui_html")
            self.browser.switch_to.frame(equation_edit_iframe)
            return (text_edit_frame, equation_edit_iframe)

        @retry_on_browser_exception(
            exceptions=(TimeoutException, JavascriptException), test_name=test_name
        )
        def add_text(text=" Some text for testing:", counter=0):
            switch_to_cke_wysiwyg_frame()
            self.wait_get_element_css("body p")
            script_code = 'document.querySelector("body p").innerText=" {} "'.format(text)
            self.browser.execute_script(script_code)

        @retry_on_browser_exception(exceptions=(TimeoutException), test_name=test_name)
        def save_equation_text_plugin():
            switch_to_text_edit_frame()

            # OK_btn
            self.click_element_css(".cke_dialog_ui_button_ok")

            # making sure that equation properly propagated, to the text editor
            switch_to_cke_wysiwyg_frame()
            self.wait_get_element_css("span.katex")

            text_edit_frame = switch_to_text_edit_frame()
            if not test_orientation:
                self.screenshot.take(
                    "equation_in_text_editor.png",
                    test_name,
                    take_screen_shot=True,
                    current_frames=(text_edit_frame,),
                )

            self.browser.switch_to.default_content()
            # save_btn
            self.click_element_css(".cms-btn.cms-btn-action.default")

        self.login_user()
        self.open_structure_board(self_test=self_test, test_name=test_name)

        self.open_stand_alone_add_modal(
            self_test=self_test, test_name=test_name, plugin_to_add="text"
        )

        add_text()

        current_frames = add_equation_text_plugin()

        self.enter_equation(
            self_test=self_test,
            tex_code=tex_code,
            font_size_value=font_size_value,
            font_size_unit=font_size_unit,
            is_inline=is_inline,
            test_name=test_name,
            not_js_injection_hack=True,
            test_orientation=test_orientation,
            current_frames=current_frames,
        )

        save_equation_text_plugin()

        self.browser.switch_to.default_content()
        self.wait_for_element_to_disappear(".cms-modal")

        self.hide_structure_mode_cms_34()

        try:
            self.wait_for_element_to_be_visible("span.katex-html")
        except (TimeoutException, NoSuchElementException):
            pass

        if not test_orientation:
            self.screenshot.take("equation_rendered.png", test_name, take_screen_shot=True)
            self.publish_and_take_screen_shot(True, test_name)

    def delete_plugin(self, delete_all=True):
        self.open_structure_board()
        delete_links = self.wait_get_elements_css("a[data-rel=delete]")
        if not delete_all:
            delete_links = [delete_links[0]]
        for _ in delete_links:
            # since the delete links aren't visible the click is triggered
            # with javascript
            self.browser.execute_script('document.querySelector("a[data-rel=delete]").click()')
            # delete_confirm
            self.click_element_css(".deletelink")

    def js_injection_hack(self):
        if USE_JS_INJECTION:
            with self.login_user_context(self.user):
                add_plugin(
                    self.placeholder,
                    "EquationPlugin",
                    language="en",
                    tex_code="js~injection~hack~for~cms<{}.{}".format(*PATCHED_CMS_VERSION_TUPLE),
                    is_inline=False,
                    font_size_value=1,
                    font_size_unit="rem",
                )
            self.browser.refresh()

    # ACTUAL TESTS

    def test_page_exists(self):
        self.browser.get(self.live_server_url)
        body = self.browser.find_element_by_css_selector("body")
        self.screenshot.take("created_page.png", "test_page_exists")
        self.assertIn("test_page", body.text)

    def test_login_user(self):
        self.login_user(take_screen_shot=True)
        self.browser.get(self.live_server_url + "/?edit")
        self.screenshot.take("start_page_user_logged_in.png", "test_login_user")
        cms_navigation = self.wait_get_element_css(".cms-toolbar-item-navigation span")
        self.assertEqual(
            cms_navigation.text,
            "example.com",
            cms_navigation.get_attribute("innerHTML"),
        )

    def test_logout_user(self):
        self.login_user()
        self.logout_user()
        self.browser.get(self.live_server_url)
        self.screenshot.take("start_page_user_logged_out.png", "test_logout_user")
        self.assertRaises(
            NoSuchElementException,
            self.browser.find_element_by_css_selector,
            "#cms-top",
        )

    def test_create_standalone_equation(self):
        self.js_injection_hack()
        self.create_standalone_equation(self_test=True)

    def test_create_standalone_equation_2rem(self):
        self.js_injection_hack()
        self.create_standalone_equation(
            font_size_value=2, test_name="test_create_standalone_equation_2rem"
        )

    def test_create_standalone_equation_1_cm(self):
        self.js_injection_hack()
        self.create_standalone_equation(
            font_size_unit="cm", test_name="test_create_standalone_equation_1_cm"
        )

    def test_create_standalone_equation_inline_True(self):
        self.js_injection_hack()
        self.create_standalone_equation(
            is_inline=True, test_name="test_create_standalone_equation_inline_True"
        )

    def test_create_standalone_mhchem_equation(self):
        self.js_injection_hack()
        self.create_standalone_equation(
            tex_code=r"\ce{A <=>>[\Delta] B3^2-_{(aq)}}",
            test_name="test_create_standalone_mhchem_equation",
        )

    def test_orientation_swap_standalone_equation(self):
        self.js_injection_hack()
        self.create_standalone_equation(
            test_orientation=True, test_name="test_orientation_swap_standalone_equation"
        )

    def test_create_text_equation(self):
        self.js_injection_hack()
        self.create_text_equation(self_test=True)

    def test_create_text_equation_2rem(self):
        self.js_injection_hack()
        self.create_text_equation(font_size_value=2, test_name="test_create_text_equation_2rem")

    def test_create_text_equation_1_cm(self):
        self.js_injection_hack()
        self.create_text_equation(font_size_unit="cm", test_name="test_create_text_equation_1_cm")

    def test_create_text_equation_inline_True(self):
        self.js_injection_hack()
        self.create_text_equation(
            is_inline=True, test_name="test_create_text_equation_inline_True"
        )

    def test_create_text_mhchem_equation(self):
        self.js_injection_hack()
        self.create_standalone_equation(
            tex_code=r"\ce{A <=>>[\Delta] B3^2-_{(aq)}}",
            test_name="test_create_text_mhchem_equation",
        )

    def test_orientation_swap_text_equation(self):
        self.js_injection_hack()
        self.create_text_equation(
            test_orientation=True, test_name="test_orientation_swap_text_equation"
        )


class TestIntegrationFirefox(TestIntegrationChrome):
    browser_port = 4445
    desire_capabilities = DesiredCapabilities.FIREFOX
    browser_name = "FireFox"
