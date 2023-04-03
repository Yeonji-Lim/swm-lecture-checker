import json
import requests
from bs4 import BeautifulSoup as bs

def job():

    LOGIN_INFO = json.load(open('login_info.json', 'r'))

    with requests.Session() as s:

        login_res = s.get('https://www.swmaestro.org/sw/member/user/forLogin.do?menuNo=200025')
        soup = bs(login_res.text, 'html.parser')
        csrf = soup.find('input', {'name': 'csrfToken'})
        print('CSRF : ', csrf['value'])

        LOGIN_INFO = {**LOGIN_INFO, **{'csrfToken': csrf['value']}}
        login_res = s.post('https://www.swmaestro.org/sw/member/user/toLogin.do', data=LOGIN_INFO)
        soup = bs(login_res.text, 'html.parser')
        password = soup.find('input', {'name': 'password'})
        print('암호화 된 비밀번호 : ', password['value'])

        LOGIN_INFO = {
            'password' : password['value'],
            'username' : LOGIN_INFO['username']
        }
        login_res = s.post('https://www.swmaestro.org/sw/login.do', data=LOGIN_INFO)
        print('로그인 요청 결과 : ', login_res.status_code)

job()