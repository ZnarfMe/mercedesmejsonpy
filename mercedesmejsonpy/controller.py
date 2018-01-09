# -*- coding: utf-8 -*-
""" Simple Mercedes me API.

Attributes:
    username (int): mercedes me username (email)
    password (string): mercedes me password
    update_interval (int): min update intervall in seconds

"""

import json
import time
from multiprocessing import RLock
import requests
import lxml.html
from mercedesmejsonpy import Exceptions as mbmeExc

SERVER_UI = "https://ui.meapp.secure.mercedes-benz.com"
SERVER_LOGIN = "https://login.secure.mercedes-benz.com"
SERVER_APP = "https://app.secure.mercedes-benz.com"

ME_STATUS_URL = "{0}/api/v1.1/me".format(SERVER_UI)
ME_LOCATION_URL = "{0}/backend/vehicles/%s/location/v2".format(SERVER_APP)
LOGIN_STEP1_URL = ME_STATUS_URL
LOGIN_STEP2_URL = '/wl/login'

CONTENT_TYPE_JSON = "application/json;charset=UTF-8"

# Set to False for testing with tools like fiddler
# Change to True for production
LOGIN_VERIFY_SSL_CERT = True

class Controller:
    """ Simple Mercedes me API.
    """
    def __init__(self, username, password, update_interval):

        self.__lock = RLock()
        self.cars = []
        self.update_interval = update_interval
        self.is_valid_session = False
        self.last_update_time = 0
        self.session = requests.session()
        self.session_cookies = self._get_session_cookies(username, password)
        if self.is_valid_session:
            self._get_cars()


    def update(self):
        """ Simple Mercedes me API.

        """
        self._get_cars()


    def get_location(self, vin):
        """ get refreshed location information.

        """
        location_response = self.session.get(ME_LOCATION_URL % vin,
                                             verify=LOGIN_VERIFY_SSL_CERT)
        return json.loads(location_response.content.decode('utf8'))['data']


    def _get_cars(self):
        cur_time = time.time()
        with self.__lock:
            if cur_time - self.last_update_time > self.update_interval:
                response = self.session.get(ME_STATUS_URL,
                                            verify=LOGIN_VERIFY_SSL_CERT)

                if response.headers["Content-Type"] == CONTENT_TYPE_JSON:
                    self.cars = json.loads(
                        response.content.decode('utf8'))['user']['vehicles']
                    self.last_update_time = time.time()


    def _get_session_cookies(self, username, password):
        # Start session and get login form.
        session = self.session
        loginpage = session.get(LOGIN_STEP1_URL, verify=LOGIN_VERIFY_SSL_CERT)

        # Get the hidden elements and put them in our form.
        login_html = lxml.html.fromstring(loginpage.text)
        hidden_elements = login_html.xpath('//form//input[@type="hidden"]')
        form = {x.attrib['name']: x.attrib['value'] for x in hidden_elements}

        # "Fill out" the form.
        form['username'] = username
        form['password'] = password
        form['remember-me'] = 1

        # login and check the values.
        url = "{0}{1}".format(SERVER_LOGIN, LOGIN_STEP2_URL)
        login_step2 = session.post(url,
                                   data=form,
                                   verify=LOGIN_VERIFY_SSL_CERT)

        login_page = lxml.html.fromstring(login_step2.text)

        hidden_elements = login_page.xpath('//form//input[@type="hidden"]')
        target_url = login_page.find(".//form").action

        # if we are on the old page, maybe the username or pw are wrong
        if target_url == "/wl/login":
            raise mbmeExc.MercedesMeException(401)

        # login correct, jump to the final page
        # and collect the right cookie
        form = {x.attrib['name']: x.attrib['value'] for x in hidden_elements}

        url = "{0}{1}".format(SERVER_LOGIN, target_url)
        final_result = session.post(url,
                                    data=form,
                                    verify=LOGIN_VERIFY_SSL_CERT)

        if final_result.headers["Content-Type"] == CONTENT_TYPE_JSON:
            # alles ok
            self.is_valid_session = True
            return session.cookies

        self.is_valid_session = False
        return None
