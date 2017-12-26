import time
import requests
import lxml.html
import json
from multiprocessing import RLock

class Controller:
    def __init__(self, username, password, update_interval):
        
        self.__lock = RLock()

        self.ME_STATUS_URL = 'https://ui.meapp.secure.mercedes-benz.com/api/v1.1/me'
        self.ME_LOCATION_URL = 'https://app.secure.mercedes-benz.com/backend/vehicles/%s/location/v2'
        self.LOGIN_VERIFY_SSL_CERT = True
        self.__last_update_time = 0
        self.session = requests.session()
        self.sessionCookies = self.__getSessionCookies(username, password)
        self.cars = []
        self.update_interval = update_interval
        self.__getCars()


    def update(self):
        self.__getCars()
    
    def getLocation(self, vin):
        locResponse = self.session.get(self.ME_LOCATION_URL % vin, verify=self.LOGIN_VERIFY_SSL_CERT)
        return json.loads(locResponse.content.decode('utf8'))['data']
        

    def __getCars(self):
        cur_time = time.time()
        with self.__lock:
            if cur_time - self.__last_update_time > self.update_interval:
                response = self.session.get(self.ME_STATUS_URL, verify=self.LOGIN_VERIFY_SSL_CERT)
                self.cars = json.loads(response.content.decode('utf8'))['user']['vehicles']
                self.__last_update_time = time.time()

    def __getSessionCookies(self, username, password):
        print("__getSessionCookies called")
        # Set to False for testing with tools like fiddler
        # Change to True for production
        LOGIN_VERIFY_SSL_CERT = self.LOGIN_VERIFY_SSL_CERT

        # GET parameters - URL we'd like to log into.

        LOGIN_URL = self.ME_STATUS_URL #'https://login.secure.mercedes-benz.com/wl/auth?rm=1&TYPE=33554432&REALMOID=06-9d5f226a-fc58-10f8-bde9-85faf120fbc2&GUID=&SMAUTHREASON=0&METHOD=GET&SMAGENTNAME=$SM$iybJ37yxs7nKlHoJtUskLPv2X3AgMbeXwfItY%2bLzSUgcYUnV1XWCUt9g8cPKZsYRtXdUqTZg%2b90efQua72CQui1uF2p%2bc0I9&TARGET=$SM$http%3a%2f%2fnewsfeed%2emeapp%2esecure%2emercedes-benz%2ecom%2fapi%2fv2%2fnewsfeed'
        LOGIN_AUTH_STEP2_URL = 'https://login.secure.mercedes-benz.com/wl/login'
        LOGIN_AUTH_STEP3_URL = 'https://login.secure.mercedes-benz.com/iap/b2c-sm-legacy-15.fcc'
        
        # Start session and get login form.
        session = self.session
        login = session.get(LOGIN_URL, verify=LOGIN_VERIFY_SSL_CERT)

        # Get the hidden elements and put them in our form.
        login_html = lxml.html.fromstring(login.text)
        hidden_elements = login_html.xpath('//form//input[@type="hidden"]')
        form = {x.attrib['name']: x.attrib['value'] for x in hidden_elements}

        # "Fill out" the form.
        form['username'] = username
        form['password'] = password
        form['remember-me'] = 1

        # Finally, login and return the session.
        loginStep2 = session.post(LOGIN_AUTH_STEP2_URL, data=form, verify=LOGIN_VERIFY_SSL_CERT)
        login_html = lxml.html.fromstring(loginStep2.text)
        hidden_elements = login_html.xpath('//form//input[@type="hidden"]')
        form = {x.attrib['name']: x.attrib['value'] for x in hidden_elements}

        loginStep3 = session.post(LOGIN_AUTH_STEP3_URL, data=form, verify=LOGIN_VERIFY_SSL_CERT)

        return session.cookies
