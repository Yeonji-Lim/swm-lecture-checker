import json
import requests
from bs4 import BeautifulSoup as bs
import schedule
import time

recent_lec = ''

def job():
    global recent_lec
    with requests.Session() as s:

        print('최근 강의 : ', recent_lec)
        json_data = json.load(open('info.json', 'r'))
        LOGIN_INFO = json_data['LOGIN_INFO']
        DISCORD_WEBHOOK_URL = json_data['DISCORD_WEBHOOK_URL']

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

        if login_res.ok:
            mentolec_page = s.get('https://www.swmaestro.org/sw/mypage/mentoLec/list.do?menuNo=200046', verify=False)
            print('멘토링 페이지 접근 결과 : ', mentolec_page.status_code)
            if mentolec_page.ok:
                soup = bs(mentolec_page.text, 'html.parser')
                new_lec = soup.select_one('#listFrm > table > tbody > tr:nth-child(1) > td.tit > div.rel > a').attrs['href']
                if recent_lec != '':
                    if new_lec != recent_lec:
                        recent_lec = new_lec
                        message = {'content':'소마에 새로운 강의가 올라왔습니다!!'}
                        requests.post(DISCORD_WEBHOOK_URL, data=message)
                else:
                    recent_lec = new_lec

schedule.every(3).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)