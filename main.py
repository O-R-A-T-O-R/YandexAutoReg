from LogPython import LogManager
from utils import YandexUser
from faker import Faker
import json

RUCAPTCHA_KEY = '88924805c88d09cd265c2e61697ec467'

valid = 'valid.txt'

"""
EXAMPLE OF REGISTRATION

for i in range(100):
    try:
        user = YandexUser(RUCAPTCHA_KEY, debug_mode=False)
        
        with open('accounts.txt', 'a', encoding='utf-8') as write_stream:
            write_stream.write(user.login + '|' + user.password + '|' + user.first_name + '|' + user.last_name + '|' + user.hint_answer + '\n')
    except Exception as e:
        LogManager.error(e, 'Не повезло (')

"""
   
"""
EXAMPLE OF EXISTENCE` CHECK

with open('accounts.txt', 'r', encoding='utf-8') as read_stream:
    rows = read_stream.readlines()
    
    for row in rows:
        row_src = row.split('|')
        
        login = row_src[0]
        password = row_src[1]
        
        user = YandexUser(RUCAPTCHA_KEY, login=login, password=password, auto_reg=False)
        
        try:
            user.authorize()
            
            print(row.rstrip('\n'), file = open(valid, 'a', encoding='utf-8'))
            
        except Exception as e:
            LogManager.error(e, ' Не повезло(')

"""