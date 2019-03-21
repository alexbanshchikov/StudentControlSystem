import time
import requests
from bs4 import BeautifulSoup as bs
import re

headers = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

def parse_1(name):
    start_time = time.time()
    URL = 'https://rasp.tpu.ru/site/campus.html'
    session = requests.Session()
    request = session.get(URL, headers=headers)
    if request.status_code == 200:
        answer = bs(request.content, 'lxml')
        print("--- %s seconds ---" % (time.time() - start_time))
        return answer.find('a', class_='text-default', text=re.compile(name)).get('href')
    else:
        print('Site unavailable')
        return 0

def parse_2(aud, URL):
    start_time = time.time()
    session = requests.Session()
    request = session.get(URL, headers=headers)
    if request.status_code == 200:
        answer = bs(request.content, 'lxml')
        print("--- %s seconds ---" % (time.time() - start_time))
        return answer.find('a', text=re.compile(aud)).get('href')
    else:
        print('Corps not entered correctly')
        return 0

def parse_3(URL):
    start_time = time.time()
    session = requests.Session()
    request = session.get(URL, headers=headers)
    if request.status_code == 200:
        answer = bs(request.content, 'lxml')
        about = []
        for div in answer.find('td', class_='cell cur-day cur-cell').find_all('div'):
            print(div.text)
            about.append(div.text)
            print("--- %s seconds ---" % (time.time() - start_time))
        return about
    else:
        return 0

start_time = time.time()
kek = parse_3(parse_2('141', parse_1('Учебный корпус № 19')))
print("--- %s seconds ---" % (time.time() - start_time))