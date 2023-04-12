import json
import requests
from bs4 import BeautifulSoup as bs
import schedule
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

recent_lec = ''
target_mento = []
recent_mento_lec = []

def job():
    global recent_lec
    with requests.Session() as s:

        if recent_lec:
            print('이전 최근 강의 : ', recent_lec)
        json_data = json.load(open('info.json', 'r'))
        LOGIN_INFO = json_data['LOGIN_INFO']
        DISCORD_WEBHOOK_URL = json_data['DISCORD_WEBHOOK_URL']

        login_res = s.get('https://www.swmaestro.org/sw/member/user/forLogin.do?menuNo=200025', verify=False)
        soup = bs(login_res.text, 'html.parser')
        csrf = soup.find('input', {'name': 'csrfToken'})
        print('CSRF : ', csrf['value'])

        LOGIN_INFO = {**LOGIN_INFO, **{'csrfToken': csrf['value']}}
        login_res = s.post('https://www.swmaestro.org/sw/member/user/toLogin.do', data=LOGIN_INFO, verify=False)
        soup = bs(login_res.text, 'html.parser')
        password = soup.find('input', {'name': 'password'})
        print('암호화 된 비밀번호 : ', password['value'])

        LOGIN_INFO = {
            'password' : password['value'],
            'username' : LOGIN_INFO['username']
        }
        login_res = s.post('https://www.swmaestro.org/sw/login.do', data=LOGIN_INFO, verify=False)
        print('로그인 요청 결과 : ', login_res.status_code)

        if login_res.ok:
            for mento in target_mento:
                mentolec_page = s.get('https://www.swmaestro.org/sw/mypage/mentoLec/list.do?menuNo=200046&searchCnd=2&searchWrd='+mento)
                print(mento, '멘토님 검색 결과 : ', mentolec_page.status_code)
                if mentolec_page.ok:
                    soup = bs(mentolec_page.text, 'html.parser')
                    mentolecs = soup.select('#listFrm > table > tbody > tr > td.tit > div.rel')
                    for mentolec in mentolecs:
                        if mentolec.find('div').text.strip() != '[마감]' and not mentolec.find('a')['href'] in recent_mento_lec:
                            recent_mento_lec.append(mentolec.find('a')['href'])
                            message = {'content': ''.join(['[[긴급]] ', mento, ' 멘토님 강의 : ',
                                                mentolec.find('a').text.strip(),
                                                '\n바로가기 : https://www.swmaestro.org', mentolec.find('a')['href']]) }
                            requests.post(DISCORD_WEBHOOK_URL, data=message, verify=False)

            mentolec_page = s.get('https://www.swmaestro.org/sw/mypage/mentoLec/list.do?menuNo=200046', verify=False)
            print('멘토링 페이지 접근 결과 : ', mentolec_page.status_code)
            if mentolec_page.ok:
                soup = bs(mentolec_page.text, 'html.parser')
                new_lec = soup.select_one('#listFrm > table > tbody > tr:nth-child(1) > td.tit > div.rel > a').attrs['href']
                new_lec_name = soup.select_one('#listFrm > table > tbody > tr:nth-child(1) > td.tit > div.rel > a').get_text().strip()
                if new_lec != recent_lec:
                    recent_lec = new_lec
                    message = {'content': ''.join(['NEW 소마 강의 : ', 
                                                new_lec_name,
                                                '\n바로가기 : https://www.swmaestro.org', new_lec]) }
                    requests.post(DISCORD_WEBHOOK_URL, data=message, verify=False)

job()
schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)