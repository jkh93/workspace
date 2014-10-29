from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (NoSuchElementException,
    StaleElementReferenceException, TimeoutException)
import time
import sys


# Default operation timeout in seconds
TIMEOUT = 10

# Default operation retry frequency
POLL_FREQUENCY = 0.5

from selenium.webdriver.remote.remote_connection import LOGGER
import logging
LOGGER.setLevel(logging.WARNING)


class Wait(WebDriverWait):
    """ Subclass of WebDriverWait with predetermined timeout and poll
    frequency.  Also deals with a wider variety of exceptions. """
    def __init__(self, driver):
        """ Constructor """
        super(Wait, self).__init__(driver, TIMEOUT, POLL_FREQUENCY)

    def until(self, method, message=''):
        """Calls the method provided with the driver as an argument until the \
        return value is not False."""
        end_time = time.time() + self._timeout
        while(True):
            try:
                value = method(self._driver)
                if value:
                    return value
            except NoSuchElementException:
                pass
            except StaleElementReferenceException:
                pass
            time.sleep(self._poll)
            if(time.time() > end_time):
                break
        raise TimeoutException(message)

    def until_not(self, method, message=''):
        """Calls the method provided with the driver as an argument until the
        return value is False."""
        end_time = time.time() + self._timeout
        while(True):
            try:
                value = method(self._driver)
                if not value:
                    return value
            except NoSuchElementException:
                return True
            except StaleElementReferenceException:
                pass
            time.sleep(self._poll)
            if(time.time() > end_time):
                break
        raise TimeoutException(message)


class LoginTests(LiveServerTestCase):
    fixtures = ['test_data.json']

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(LoginTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LoginTests, cls).tearDownClass()

    def get(self, relative_url):
        self.selenium.get('%s%s' % (self.live_server_url, relative_url))

    def enter_text(self, name, value):
        field = self.wait_for_element_by_name(name)
        field.send_keys(value)
        return field

    def wait_for_element_by_name(self, name):
        element_is_present = lambda driver: driver.find_element_by_name(name)
        msg = "An element named '%s' should be on the page" % name
        element = Wait(self.selenium).until(element_is_present, msg)
        return element

    def test_uc010101_01_login_positive(self):
        self.get('/')
        self.enter_text('username', 'nathan')
        self.enter_text('password', '13ceecos')
        self.selenium.find_element_by_xpath('//input[@value="Log In"]').click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('home', body.get_attribute("id"))
        el = self.selenium.find_element_by_link_text('User Tools')
        el.click()
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text('LOG OUT')
        el.click()
        self.selenium.implicitly_wait(2)
        username = self.selenium.find_element_by_id('id_username')
        password = self.selenium.find_element_by_id('id_password')
        self.assertIsNotNone(username)
        self.assertIsNotNone(password)

    def test_uc010101_02_login_no_user_name(self):
        self.get('/')
        self.enter_text('username', '')
        self.enter_text('password', '13ceecos')
        self.selenium.find_element_by_xpath('//input[@value="Log In"]').click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('This field is required', body.text)

    def test_uc010101_03_login_no_password(self):
        self.get('/')
        self.enter_text('username', 'nathan')
        self.enter_text('password', '')
        self.selenium.find_element_by_xpath('//input[@value="Log In"]').click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('This field is required', body.text)

    def test_uc010101_04_login_incorrect_user_name(self):
        self.get('/')
        self.enter_text('username', 'nathanxyz')
        self.enter_text('password', '13ceecos')
        self.selenium.find_element_by_xpath('//input[@value="Log In"]').click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('Please enter a correct username and password',
                      body.text)

    def test_uc010101_05_login_incorrect_password(self):
        self.get('/')
        self.enter_text('username', 'nathan')
        self.enter_text('password', 'abc123')
        self.selenium.find_element_by_xpath('//input[@value="Log In"]').click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('Please enter a correct username and password',
                      body.text)


class PasswordTests(LiveServerTestCase):
    fixtures = ['test_data.json']

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(PasswordTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(PasswordTests, cls).tearDownClass()

    def setUp(self):
        self.get('/')
        self.enter_text('username', 'nathan')
        self.enter_text('password', '13ceecos')
        self.selenium.find_element_by_xpath('//input[@value="Log In"]').click()

    def get(self, relative_url):
        self.selenium.get('%s%s' % (self.live_server_url, relative_url))

    def enter_text(self, name, value):
        field = self.wait_for_element_by_name(name)
        field.send_keys(value)
        return field

    def wait_for_element_by_name(self, name):
        element_is_present = lambda driver: driver.find_element_by_name(name)
        msg = "An element named '%s' should be on the page" % name
        element = Wait(self.selenium).until(element_is_present, msg)
        return element

    def test_uc010202_01_change_password(self):
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text('User Tools')
        el.click()
        el = self.selenium.find_element_by_link_text('CHANGE PASSWORD')
        el.click()
        self.selenium.implicitly_wait(2)
        self.enter_text('old_password', '13ceecos')
        self.enter_text('new_password1', 'password')
        self.enter_text('new_password2', 'password')
        self.selenium.find_element_by_xpath('//input[@value="Change Password"]').click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('Password Change Successful', body.text)
        self.get('/')
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text('User Tools')
        el.click()
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text('LOG OUT')
        el.click()
        self.selenium.implicitly_wait(2)
        self.enter_text('username', 'nathan')
        self.enter_text('password', 'password')
        self.selenium.find_element_by_xpath('//input[@value="Log In"]').click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('home', body.get_attribute("id"))


class ProfileTests(LiveServerTestCase):
    fixtures = ['test_data.json']

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(ProfileTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(ProfileTests, cls).tearDownClass()

    def setUp(self):
        self.get('/')
        self.enter_text('username', 'nathan')
        self.enter_text('password', '13ceecos')
        self.selenium.find_element_by_xpath('//input[@value="Log In"]').click()

    def get(self, relative_url):
        self.selenium.get('%s%s' % (self.live_server_url, relative_url))

    def enter_text(self, name, value):
        field = self.wait_for_element_by_name(name)
        field.clear()
        field.send_keys(value)
        return field

    def wait_for_element_by_name(self, name):
        element_is_present = lambda driver: driver.find_element_by_name(name)
        msg = "An element named '%s' should be on the page" % name
        element = Wait(self.selenium).until(element_is_present, msg)
        return element

    def test_uc010302_01_edit_profile_username(self):
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text('User Tools')
        el.click()
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text('PROFILE')
        el.click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('USER PROFILE', body.text)
        self.enter_text('username', 'test')
        self.selenium.find_element_by_xpath('//input[@value="Save"]').click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('home', body.get_attribute("id"))
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text('User Tools')
        el.click()
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text('LOG OUT')
        el.click()
        self.selenium.implicitly_wait(2)
        self.enter_text('username', 'test')
        self.enter_text('password', '13ceecos')
        self.selenium.find_element_by_xpath('//input[@value="Log In"]').click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('home', body.get_attribute("id"))

#    def test_uc010302_02_edit_profile_first_name(self):
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('User Tools')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('PROFILE')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        body = self.selenium.find_element_by_tag_name('body')
#        self.assertIn('User Profile', body.text)
#        self.enter_text('first_name', 'test')
#        self.selenium.find_element_by_xpath('//input[@value="Save"]').click()
#        self.selenium.implicitly_wait(2)
#        title = self.selenium.find_element_by_tag_name('title')
#        self.assertIn('Home', title.text)
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('User Tools')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('PROFILE')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        first_name = self.selenium.find_element_by_id('id_first_name')
#        self.assertIn('test', first_name.get_attribute('value'))
#
#    def test_uc010302_03_edit_profile_last_name(self):
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('User Tools')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('PROFILE')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        body = self.selenium.find_element_by_tag_name('body')
#        self.assertIn('User Profile', body.text)
#        self.enter_text('last_name', 'test')
#        self.selenium.find_element_by_xpath('//input[@value="Save"]').click()
#        self.selenium.implicitly_wait(2)
#        title = self.selenium.find_element_by_tag_name('title')
#        self.assertIn('Home', title.text)
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('User Tools')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('PROFILE')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        last_name = self.selenium.find_element_by_id('id_last_name')
#        self.assertIn('test', last_name.get_attribute('value'))
#
#    def test_uc010302_04_edit_profile_email(self):
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('User Tools')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('PROFILE')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        body = self.selenium.find_element_by_tag_name('body')
#        self.assertIn('User Profile', body.text)
#        self.enter_text('email', 'test@test.com')
#        self.selenium.find_element_by_xpath('//input[@value="Save"]').click()
#        self.selenium.implicitly_wait(2)
#        title = self.selenium.find_element_by_tag_name('title')
#        self.assertIn('Home', title.text)
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('User Tools')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('PROFILE')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        email = self.selenium.find_element_by_id('id_email')
#        self.assertIn('test@test.com', email.get_attribute('value'))
#
#    def test_uc010302_05_edit_profile_no_username(self):
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('User Tools')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('PROFILE')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        body = self.selenium.find_element_by_tag_name('body')
#        self.assertIn('User Profile', body.text)
#        self.enter_text('username', '')
#        self.selenium.find_element_by_xpath('//input[@value="Save"]').click()
#        self.selenium.implicitly_wait(2)
#        body = self.selenium.find_element_by_tag_name('body')
#        self.assertIn('This field is required', body.text)
#
#    def test_uc010302_06_edit_profile_no_first_name(self):
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('User Tools')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('PROFILE')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        body = self.selenium.find_element_by_tag_name('body')
#        self.assertIn('User Profile', body.text)
#        self.enter_text('first_name', '')
#        self.selenium.find_element_by_xpath('//input[@value="Save"]').click()
#        self.selenium.implicitly_wait(2)
#        title = self.selenium.find_element_by_tag_name('title')
#        self.assertIn('Home', title.text)
#
#    def test_uc010302_07_edit_profile_no_last_name(self):
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('User Tools')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        el = self.selenium.find_element_by_link_text('PROFILE')
#        el.click()
#        self.selenium.implicitly_wait(2)
#        body = self.selenium.find_element_by_tag_name('body')
#        self.assertIn('User Profile', body.text)
#        self.enter_text('last_name', '')
#        self.selenium.find_element_by_xpath('//input[@value="Save"]').click()
#        self.selenium.implicitly_wait(2)
#        title = self.selenium.find_element_by_tag_name('title')
#        self.assertIn('Home', title.text)

    def test_uc010302_08_edit_profile_no_email(self):
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text('User Tools')
        el.click()
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text('PROFILE')
        el.click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('USER PROFILE', body.text)
        self.enter_text('email', '')
        self.selenium.find_element_by_xpath('//input[@value="Save"]').click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('This field is required', body.text)


class CreateBrewTests(LiveServerTestCase):
    fixtures = ['test_data.json']

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(CreateBrewTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(CreateBrewTests, cls).tearDownClass()

    def setUp(self):
        self.get('/')
        self.enter_text('username', 'nathan')
        self.enter_text('password', '13ceecos')
        self.selenium.find_element_by_xpath('//input[@value="Log In"]').click()

    def get(self, relative_url):
        self.selenium.get('%s%s' % (self.live_server_url, relative_url))

    def enter_text(self, name, value):
        field = self.wait_for_element_by_name(name)
        field.clear()
        field.send_keys(value)
        return field

    def wait_for_element_by_name(self, name):
        element_is_present = lambda driver: driver.find_element_by_name(name)
        msg = "An element named '%s' should be on the page" % name
        element = Wait(self.selenium).until(element_is_present, msg)
        return element

    def select_menu(self, menu, submenu):
        el = self.selenium.find_element_by_link_text(menu)
        el.click()
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text(submenu)
        el.click()
        self.selenium.implicitly_wait(2)

    def verify_menu_items(self, name, options_list):
        select = Select(self.selenium.find_element_by_name(name))
        self.assertEqual(options_list[0], select.first_selected_option.text)

        options = select.options
        for option in options[:]:
            for item in options_list[:]:
                if item == option.text:
                    self.assertEqual(item, option.text)
                    options_list.remove(item)
                    options.remove(option)
        self.assertEqual(0, len(options_list))
        self.assertEqual(0, len(options))
        return select.options

    def test_uc020201_01_create_brew_from_menu(self):
        bev_types = ['---------', 'Lager', 'Stout']
        product_types = ['Lager']
        dest_tanks = ['---------', 'FV1', 'FV2', 'FV3', 'CT1']
        blend_withs = ['---------']
        self.selenium.implicitly_wait(2)
        self.select_menu('Production', 'BREW')
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('brew_list', body.get_attribute("id"))
        el = self.selenium.find_element_by_link_text('CREATE BREW')
        el.click()
        self.selenium.implicitly_wait(2)
        self.enter_text('create_date', '01/01/2013')
        options = self.verify_menu_items('bev_type', bev_types)

        for option in options:
            if option.text == 'Lager':
                option.click()
                break

        select = self.selenium.find_element_by_name('product_type')
        self.assertEqual(False, select.is_displayed())

        self.enter_text('yeast', 'WY3068')
        self.enter_text('starting_density', '1.042')

        options = self.verify_menu_items('dest_tank', dest_tanks)

        for option in options:
            if option.text == 'FV2':
                option.click()
                break

        select = self.selenium.find_element_by_name('blend_with')
        self.assertEqual(False, select.is_displayed())

        self.enter_text('dest_volume', '5000')

        self.selenium.find_element_by_xpath(
            '//input[@value="Save Brew"]').click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('brew_list', body.get_attribute("id"))
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text('Home')
        el.click()
        self.selenium.implicitly_wait(2)
        while True:
            self.selenium.find_element_by_class_name('fc-button-prev').click()
            self.selenium.implicitly_wait(2)
            date_title = self.selenium.find_element_by_class_name('fc-tue')
            if date_title.text == 'TUE 1/1':
                event = self.selenium.find_element_by_class_name(
                    'fc-event-title')
                self.assertIn('Brew: Lager', event.text)
                break

        self.selenium.implicitly_wait(2)
        self.select_menu('Reports', 'BREWS')
        self.selenium.implicitly_wait(2)
        table = self.selenium.find_element_by_tag_name('table')
        self.assertIn('Lager', table.text)
        self.assertIn('1.042', table.text)
        self.assertIn('Jan. 1, 2013', table.text)

        self.select_menu('Reports', 'CURRENT TANKS')
        self.selenium.implicitly_wait(2)
        table = self.selenium.find_element_by_tag_name('table')
        self.assertIn('FV2', table.text)
        self.assertIn('LG1', table.text)
        self.assertIn('Lager', table.text)
        self.assertIn('Fermenting', table.text)
        self.assertIn('Jan. 1, 2013', table.text)
        self.assertIn('50.0', table.text)


class CreateTransferTests(LiveServerTestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(CreateTransferTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(CreateTransferTests, cls).tearDownClass()

    def setUp(self):
        self.get('/')
        self.enter_text('username', 'nathan')
        self.enter_text('password', '13ceecos')
        self.selenium.find_element_by_xpath('//input[@value="Log In"]').click()

    def get(self, relative_url):
        self.selenium.get('%s%s' % (self.live_server_url, relative_url))

    def enter_text(self, name, value):
        field = self.wait_for_element_by_name(name)
        field.clear()
        field.send_keys(value)
        return field

    def wait_for_element_by_name(self, name):
        element_is_present = lambda driver: driver.find_element_by_name(name)
        msg = "An element named '%s' should be on the page" % name
        element = Wait(self.selenium).until(element_is_present, msg)
        return element

    def select_menu(self, menu, submenu):
        el = self.selenium.find_element_by_link_text(menu)
        el.click()
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text(submenu)
        el.click()
        self.selenium.implicitly_wait(2)

    def verify_menu_items(self, name, options_list):
        select = Select(self.selenium.find_element_by_name(name))
        self.assertEqual(options_list[0], select.first_selected_option.text)

        options = select.options
        for option in options[:]:
            for item in options_list[:]:
                if item == option.text:
                    self.assertEqual(item, option.text)
                    options_list.remove(item)
                    options.remove(option)
                    break
        self.assertEqual(0, len(options_list))
        self.assertEqual(0, len(options))
        return select

    def test_uc020101_02_transfer_from_menu(self):
        cur_tanks = ['---------', 'FV2: Lager (LG1)']
        dest_tanks = ['---------', 'FV1', 'FV2', 'FV3', 'CT1']
        product_types = ['Lager', 'Stout', '---------']
        self.selenium.implicitly_wait(2)
        self.select_menu('Production', 'TRANSFER')
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('transfer_list', body.get_attribute("id"))
        el = self.selenium.find_element_by_link_text('CREATE TRANSFER')
        el.click()
        self.selenium.implicitly_wait(2)
        self.enter_text('transfer_date', '02/01/2013')

        options = self.verify_menu_items('cur_tank', cur_tanks).options

        for option in options:
            if option.text == 'FV2: Lager (LG1)':
                option.click()
                break

        self.selenium.implicitly_wait(2)

        self.assertEqual(False,
            self.selenium.find_element_by_name('empty').is_selected())

        select = self.verify_menu_items('dest_tank', dest_tanks)

        for option in select.options:
            if option.text == 'CT1':
                option.click()
                break

        select = self.selenium.find_element_by_name('blend_with')
        self.assertEqual(False, select.is_displayed())

        select = self.verify_menu_items('product_type', product_types)

        self.assertEqual('Lager', select.first_selected_option.text)

        self.enter_text('dest_volume', '2000')

        self.selenium.implicitly_wait(2)
        self.selenium.find_element_by_xpath(
            '//input[@value="Save Transfer"]').click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('transfer_list', body.get_attribute("id"))
        el = self.selenium.find_element_by_link_text('Home')
        el.click()
        self.selenium.implicitly_wait(2)
        while True:
            self.selenium.find_element_by_class_name('fc-button-prev').click()
            self.selenium.implicitly_wait(2)
            date_title = self.selenium.find_element_by_class_name('fc-wed')
            if 'WED 2/1' == date_title.text:
                event = self.selenium.find_element_by_class_name('fc-view')
                self.assertIn('Transfer: LG1 to CT1', event.text)
                break

        self.select_menu('Reports', 'CURRENT TANKS')
        self.selenium.implicitly_wait(2)
        table = self.selenium.find_element_by_tag_name('table')
        self.assertIn('FV2', table.text)
        self.assertIn('LG1', table.text)
        self.assertIn('Lager', table.text)
        self.assertIn('Fermenting', table.text)
        self.assertIn('Jan. 1, 2013', table.text)
        self.assertIn('30.0', table.text)
        self.assertIn('CT1', table.text)
        self.assertIn('LG1', table.text)
        self.assertIn('Lager', table.text)
        self.assertIn('Fermenting', table.text)
        self.assertIn('Jan. 2, 2013', table.text)
        self.assertIn('20.0', table.text)


class CreatePackageTests(LiveServerTestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(CreatePackageTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(CreatePackageTests, cls).tearDownClass()

    def setUp(self):
        self.get('/')
        self.enter_text('username', 'nathan')
        self.enter_text('password', '13ceecos')
        self.selenium.find_element_by_xpath('//input[@value="Log In"]').click()

    def get(self, relative_url):
        self.selenium.get('%s%s' % (self.live_server_url, relative_url))

    def enter_text(self, name, value):
        field = self.wait_for_element_by_name(name)
        field.clear()
        field.send_keys(value)
        return field

    def wait_for_element_by_name(self, name):
        element_is_present = lambda driver: driver.find_element_by_name(name)
        msg = "An element named '%s' should be on the page" % name
        element = Wait(self.selenium).until(element_is_present, msg)
        return element

    def select_menu(self, menu, submenu):
        el = self.selenium.find_element_by_link_text(menu)
        el.click()
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text(submenu)
        el.click()
        self.selenium.implicitly_wait(2)

    def verify_menu_items(self, name, options_list):
        select = Select(self.selenium.find_element_by_name(name))
        self.assertEqual(options_list[0], select.first_selected_option.text)

        options = select.options
        for option in options[:]:
            for item in options_list[:]:
                if item == option.text:
                    self.assertEqual(item, option.text)
                    options_list.remove(item)
                    options.remove(option)
                    break
        self.assertEqual(0, len(options_list))
        self.assertEqual(0, len(options))
        return select

    def test_uc020103_01_package_from_menu(self):
        bev_tanks = ['---------', 'FV2: Lager (LG1)']
        package_types = ['---------', '50L Keg', '30L Keg', '20L Bag',
            '40L Cask', '330mL Bottle', '500mL Bottle', 'Tank']
        self.selenium.implicitly_wait(2)
        self.select_menu('Production', 'PACKAGE')
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('package_list', body.get_attribute("id"))
        el = self.selenium.find_element_by_link_text("CREATE PACKAGE")
        el.click()
        self.enter_text('create_date', '03/01/2013')

        options = self.verify_menu_items('bev_tank', bev_tanks).options

        for option in options:
            if option.text == 'FV2: Lager (LG1)':
                option.click()
                break

        self.assertEqual(False,
            self.selenium.find_element_by_name('empty').is_selected())

        select = self.verify_menu_items('package_type', package_types)

        for option in select.options:
            if option.text == '50L Keg':
                option.click()
                break

        self.enter_text('item_count', '10')

        self.selenium.implicitly_wait(2)
        self.selenium.find_element_by_xpath('//input[@value="Save Package"]').click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('package_list', body.get_attribute("id"))
        el = self.selenium.find_element_by_link_text('Home')
        el.click()
        self.selenium.implicitly_wait(2)
        while True:
            self.selenium.find_element_by_class_name('fc-button-prev').click()
            self.selenium.implicitly_wait(2)
            date_title = self.selenium.find_element_by_class_name('fc-thu')
            if date_title.text == 'THU 3/1':
                event = self.selenium.find_element_by_class_name('fc-view')
                self.assertIn('Package: Lager', event.text)
                break

        self.select_menu('Reports', 'CURRENT TANKS')
        self.selenium.implicitly_wait(2)
        table = self.selenium.find_element_by_tag_name('table')
        self.assertIn('FV2', table.text)
        self.assertIn('LG1', table.text)
        self.assertIn('Lager', table.text)
        self.assertIn('Fermenting', table.text)
        self.assertIn('Jan. 1, 2013', table.text)
        self.assertIn('50.0', table.text)
        self.assertIn('45.0', table.text)
        self.assertIn('5.0', table.text)


class CreateMeasurementTests(LiveServerTestCase):
    fixtures = ['test_data.json', 'test_data_brew.json']

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(CreateMeasurementTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(CreateMeasurementTests, cls).tearDownClass()

    def setUp(self):
        self.get('/')
        self.enter_text('username', 'nathan')
        self.enter_text('password', '13ceecos')
        self.selenium.find_element_by_xpath('//input[@value="Log In"]').click()

    def get(self, relative_url):
        self.selenium.get('%s%s' % (self.live_server_url, relative_url))

    def enter_text(self, name, value):
        field = self.wait_for_element_by_name(name)
        field.clear()
        field.send_keys(value)
        return field

    def wait_for_element_by_name(self, name):
        element_is_present = lambda driver: driver.find_element_by_name(name)
        msg = "An element named '%s' should be on the page" % name
        element = Wait(self.selenium).until(element_is_present, msg)
        return element

    def select_menu(self, menu, submenu):
        el = self.selenium.find_element_by_link_text(menu)
        el.click()
        self.selenium.implicitly_wait(2)
        el = self.selenium.find_element_by_link_text(submenu)
        el.click()
        self.selenium.implicitly_wait(2)

    def verify_menu_items(self, name, options_list):
        select = Select(self.selenium.find_element_by_name(name))
        self.assertEqual(options_list[0], select.first_selected_option.text)

        options = select.options
        for option in options[:]:
            for item in options_list[:]:
                if item == option.text:
                    self.assertEqual(item, option.text)
                    options_list.remove(item)
                    options.remove(option)
                    break
        self.assertEqual(0, len(options_list))
        self.assertEqual(0, len(options))
        return select

    def test_uc020103_01_package_from_menu(self):
        bev_tanks = ['---------', 'FV2: Lager (LG1)']
        measurement_types = ['---------', 'Volume', 'Density', 'Alcohol',
            'Set Temperature', 'Actual Temperature', 'CO2', 'O2', 'Pressure']
        self.selenium.implicitly_wait(2)
        self.select_menu('Production', 'MEASUREMENT')
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('measurement_list', body.get_attribute("id"))
        el = self.selenium.find_element_by_link_text("CREATE MEASUREMENT")
        el.click()
        self.enter_text('measurement_date', '03/01/2013')

        options = self.verify_menu_items(
            'measurement_type', measurement_types).options

        for option in options:
            if option.text == 'Density':
                option.click()
                break

        options = self.verify_menu_items('bev_tank', bev_tanks).options

        for option in options:
            if option.text == 'FV2: Lager (LG1)':
                option.click()
                break

        self.enter_text('value', '1.0125')

        self.selenium.find_element_by_xpath('//input[@value="Save Measurement"]').click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('measurement_list', body.get_attribute("id"))
        el = self.selenium.find_element_by_link_text("Home")
        el.click()

        while True:
            self.selenium.find_element_by_class_name('fc-button-prev').click()
            self.selenium.implicitly_wait(2)
            date_title = self.selenium.find_element_by_class_name('fc-thu')
            if date_title.text == 'THU 3/1':
                events = self.selenium.find_elements_by_class_name(
                    'fc-event-inner')
                for event in events:
                    if 'Brew: Lager' in event.text:
                        self.assertIn('Brew: Lager', event.text)
                        event.click()
                        break
                break
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('BrewDetailView', body.get_attribute("id"))
        el = self.selenium.find_element_by_css_selector('.brew-detail-summary')
        el.click()
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('brew_detail', body.get_attribute("id"))
        trs = self.selenium.find_elements_by_tag_name('tr')
        for tr in trs:
            if 'Jan 1, 2013' in tr.text:
                self.assertIn('1.042', tr.text)
            if 'Jan 3, 2013' in tr.text:
                self.assertIn('1.0125', tr.text)
                break
        self.select_menu('Production', 'PACKAGE')
        el = self.selenium.find_element_by_link_text('CREATE PACKAGE')
        el.click()
        self.selenium.implicitly_wait(2)
        self.enter_text('create_date', '04/01/2013')

        select = Select(self.selenium.find_element_by_name('bev_tank'))
        for option in select.options:
            if option.text == 'FV2: Lager (LG1)':
                option.click()
                break

        select = Select(self.selenium.find_element_by_name('package_type'))
        for option in select.options:
            if option.text == '50L Keg':
                option.click()
                break

        self.enter_text('item_count', '10')

        self.selenium.implicitly_wait(2)
        self.selenium.find_element_by_xpath(
            '//input[@value="Save Package"]').click()

        self.selenium.implicitly_wait(2)
        self.select_menu('Production', 'CHECKOUT')
        el = self.selenium.find_element_by_link_text('CREATE CHECKOUT')
        el.click()
        self.selenium.implicitly_wait(2)
        self.enter_text('create_date', '05/01/2013')

        select = Select(self.selenium.find_element_by_name('package'))
        for option in select.options:
            if option.text == 'LG1: 50L Keg (10.0 in stock)':
                option.click()
                break

        self.selenium.implicitly_wait(2)

        self.enter_text('item_count', '10')

        self.selenium.implicitly_wait(2)
        self.selenium.find_element_by_xpath('//input[@value="Save Checkout"]').click()
        self.selenium.implicitly_wait(2)

        self.select_menu('Customs', 'CREATE SUBMISSION')
        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('submission_create', body.get_attribute("id"))

        self.enter_text('start_date', '1/1/2013')
        self.enter_text('end_date', '31/1/2013')
        self.selenium.find_element_by_xpath(
            '//input[@value="View Draft Submission"]').click()

        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('submission_complete', body.get_attribute("id"))
        trs = self.selenium.find_elements_by_tag_name('tr')
        for tr in trs:
            if 'LG1: 50L Keg (04 Jan)' in tr.text:
                self.assertIn('Jan. 5, 2013', tr.text)
                self.assertIn('500.0', tr.text)
                self.assertIn('False', tr.text)
                break
        else:
            self.assertTrue(False, 'No checkout found in Submission')
        self.selenium.implicitly_wait(2)
        self.selenium.find_element_by_xpath(
            '//input[@value="Confirm and Submit"]').click()

        self.selenium.implicitly_wait(2)
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('submission_detail', body.get_attribute("id"))

        trs = self.selenium.find_elements_by_tag_name('tr')
        for tr in trs:
            if 'Lager' in tr.text:
                self.assertIn('500.0', tr.text)
                break
        else:
            self.assertTrue(False, 'No volume found in Submission')

