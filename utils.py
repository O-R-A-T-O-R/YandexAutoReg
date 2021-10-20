"""
https://ru.stackoverflow.com/questions/1239229/%D0%90%D0%B2%D1%82%D0%BE%D1%80%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D0%BD%D0%B0-%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81-%D1%81-%D0%BF%D0%BE%D0%BC%D0%BE%D1%89%D1%8C%D1%8E-python
"""

import json
import requests
from fake_useragent import UserAgent
from base64 import b64encode
from time import sleep
from json import loads
from bs4 import BeautifulSoup
from LogPython import LogManager
import re
from faker import Faker

class YandexUser:    
    YANDEX_REGISTRATION_FIELDS = 'https://passport.yandex.ru/registration'
    YANDEX_REGISTRATION = 'https://passport.yandex.ru/registration-validations/registration-alternative'
    CHECK_HUMAN = 'https://passport.yandex.ru/registration-validations/checkHuman'
    YANDEX_AUTHORIZATION = "https://passport.yandex.com/auth"
    
    user = UserAgent().random
    HEADERS = {
        'User-Agent' : user,
        "X-Requested-With": "XMLHttpRequest"
    }

    session = requests.Session()
    session.headers = HEADERS
    faker_ = Faker('ru_RU')
    
    def __init__(self, 
                 ru_captcha_key : str = None,
                 first_name : str = None,
                 last_name : str = None,
                 login : str = None,
                 password : str = None,
                 hint_answer : str = None,
                 **kwargs):

        self.ru_captcha_key = ru_captcha_key
        self.first_name = first_name if first_name else self.faker_.first_name()
        self.last_name = last_name if last_name else self.faker_.last_name()
        self.login = (login if login else self.faker_.user_name() + self.faker_.md5()[:4]).replace('_', '')
        self.password = password if password else self.faker_.password()
        self.hint_answer = hint_answer if hint_answer else self.faker_.md5()[:10]
        
        self.debug_mode = kwargs.get('debug_mode') if 'debug_mode' in kwargs.keys() else True
        self.auto_reg = kwargs.get('auto_reg') if 'auto_reg' in kwargs else True

        if not self.auto_reg:
            return

        ya_body = self.session.get(self.YANDEX_REGISTRATION_FIELDS).text
        soup = BeautifulSoup(ya_body, 'html.parser')

        track_id = soup.find('input', {'name' : 'track_id'}).attrs['value']
        csrf_token = re.search(r'"csrf":"(.{54})"', ya_body).group(1)
            
        req0 = self.session.post('https://passport.yandex.ru/registration-validations/textcaptcha', data = {
            'track_id' : track_id,
            'csrf_token' : csrf_token,
            'language' : 'ru',
            'ocr' : 'true'
        })
        
        try:
            captcha_solution = self.solve_captcha(loads(req0.text).get('image_url'))
        except:
            raise Exception('CaptchaSolving Exception [i]')
            
        captcha_data = {
            'track_id' : track_id,
            'csrf_token' : csrf_token,
            'answer' : captcha_solution
        }

        self.reg_data = {
            'track_id' : track_id,
            'csrf_token' : csrf_token,
            'firstname' : self.first_name,
            'lastname' : self.last_name,
            'surname' : '',                                 
            'login' : self.login,
            'password' : self.password,
            'password_confirm' : self.password,
            'hint_question_id': '12',
            'hint_question': 'Фамилия вашего любимого музыканта',
            'hint_question_custom': '',
            'hint_answer': self.hint_answer,
            'captcha': captcha_solution,
            'phone': '',
            'phoneCode': '',
            'publicId': '',
            'human-confirmation': 'captcha',
            'eula_accepted': 'on',
            'type': 'alternative'
        }

        request = self.session.post(self.CHECK_HUMAN, data = captcha_data)
        request2 = self.session.post(self.YANDEX_REGISTRATION, data = self.reg_data)
        
        if loads(request2.text).get('status') == 'error':
            raise Exception('UserData Exception -> ' + str(loads(request2.text).get('error')[0].get('message') + '<--->' + request2.text))

        if loads(request.text).get('status') == 'error':
            raise Exception('SolveCaptcha Exception -> ' + str(loads(request.text).get('errors')))

        LogManager.info(self.login, self.password, 'Successfully created [+]')
        
    def solve_captcha(self, captcha_link):
        POST_LINK = 'http://rucaptcha.com/in.php'
        GET_LINK = 'http://rucaptcha.com/res.php'

        captcha_64 = b64encode(self.session.get(captcha_link).content)

        request_data = {
            'key' : self.ru_captcha_key,
            'method' : 'base64',
            'body' : captcha_64
        }

        captcha = (self.session.post(POST_LINK, data = request_data).text).split('|')

        LogManager.info(self.login, self.password, 'Status: ', captcha[0])
        captcha_id = captcha[1]

        captcha_solution_link = GET_LINK + '?key=' + self.ru_captcha_key + '&action=get&json=1' + '&id=' + str(captcha_id)

        retries = 0
        while 'I am waiting CAPTCHA solution':
            captcha_solution = loads(self.session.get(captcha_solution_link).text)

            if captcha_solution.get('status') == 1:
                if self.debug_mode:
                    LogManager.info('I found captcha solution: ', captcha_solution.get('request'))
                break

            if self.debug_mode:
                LogManager.warning('I am waiting CAPTCHA solution (1000ms)')

            if retries >= 6:
                break

            retries += 1
            sleep(1)
            
        return captcha_solution.get('request')
    
    def authorize(self):
        auth_data = {
            'login': self.login,
            'passwd': self.password,
        }
        
        response = self.session.post(self.YANDEX_AUTHORIZATION, data = auth_data)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if soup.title.text == 'Authorization':
            raise Exception('UserData Exception ')
        else:
            if self.debug_mode:
                LogManager.info(self.login, self.password, 'Successfully logged in [+]')
        
        