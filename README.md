# swm-lecture-checker

SWM 멘토링 게시판의 새로운 멘토특강 알림봇 (Discord)

누구보다 빠르게 멘토특강을 신청하고 싶어서 만들었습니다.

일단은 알림봇이지만, 만약 얘를 쓰고 나서도 특강을 놓친다면,, 그때는 그냥 신청까지 해주게 만들랍니다..

소마는 일부러 이렇게 개발하게 하려고 알림을 안해주는 걸까요? ㅎ..

크롤링은 잘 안해봐서 이런저런 공부와 함께 개발 해보았습니다.

3분마다 소마 특강 페이지 훑어보고 목록에 변화가 있으면 제일 최근 강의를 바로가기 링크와 함께 알려줍니다!

<img width="975" alt="image" src="https://user-images.githubusercontent.com/57888020/231365627-9bcc5768-47b0-40cd-b845-80cd3effa426.png">

요청이 있으면 새로운 강의 목록을 알려주는 것으로 바꿔보겠습니다

## Quick Start

- clone 및 패키지 설치
    ```sh
    git clone https://github.com/Yeonji-Lim/swm-lecture-checker.git
    cd swm-lecture-checker
    pip install -r requirements.txt
    ```

- `info.json`을 맞는 값으로 채워주세요

    [디스코드 웹훅 URL 참고](https://support.discord.com/hc/ko/articles/228383668-%EC%9B%B9%ED%9B%85%EC%9D%84-%EC%86%8C%EA%B0%9C%ED%95%A9%EB%8B%88%EB%8B%A4)

- PC 종료 전까지 실행하기
    ```sh
    python3 main.py
    ```

    그런데 이렇게 되면 개인 PC가 켜져있는 동안 이 파일을 실행시켜야만 알림을 주게 되므로, 

    따로 서버에 등록해서 사용하시는 것이 좋습니다.

### 특정 멘토님 강의 체크하기

- main.py 내의 target_mento list에 멘토님 이름을 적은 후 실행합니다.
    ```python
    target_mento = ['임연지', '이종범']
    ```

---
<details>
<summary>개발 과정 보기</summary>

### 로그인 분석하기

이 부분은 공부의 차원에서 적습니다.

먼저 멘토링 게시판은 연수생이 로그인을 해야 볼 수 있으므로, 파이썬으로 로그인을 해주어야 합니다.

그러기 위해서는 SWM에서는 로그인을 어떻게 수행하는지 이해해야 합니다.

먼저 개발자도구 요소 탭에서 로그인 박스 부분이 어떻게 되어있는지 파악합니다.
![](https://i.imgur.com/g6KZm1U.png)

폼 안에 `input`으로 `loginFlag`, `menuNo`, `csrfToken`, `username`, `password` 등이 있는 것을 확인할 수 있어요

![](https://i.imgur.com/05OjUmq.png)

로그인 창에서 아이디 비번을 입력해놓고, 

개발자도구의 네트워크 탭에서 🚫 눌러서 기록을 없애 줍니다.

로그인이 성공하고 나면 페이지 리다이렉션이 있기 때문에 로그가 초기화되지 않도록 `로그 보존`을 체크해줍니다.

그리고 나서 로그인을 해줍니다.

그렇게 했을 때 로그를 보면 toLogin.do, login.do로 차례로 요청을 보내는 것을 볼 수 있어요

toLogin.do의 페이로드

```
loginFlag:
menuNo: 200025
csrfToken: 토큰 값
username: 계정
password: 비번
id: on
```

login.do의 페이로드

```
password: 암호화된 비번
username: 계정
```

크롤링으로 접근할 때도 차례로 저 값들로 요청을 해야한다는 것입니다..!

결론적으로 다음과 같이 로그인 접근을 할 수 있습니다.

```python
with requests.Session() as s:

    json_data = json.load(open('info.json', 'r'))
    LOGIN_INFO = json_data['LOGIN_INFO']

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
```

### Discord 알림봇 생성 및 연동

[이 페이지](https://coffee4m.com/%EB%94%94%EC%8A%A4%EC%BD%94%EB%93%9C-%EB%A9%94%EC%8B%A0%EC%A0%80-%EC%95%8C%EB%A6%BC-%EB%B4%87/)를 참고하였습니다.

</details>
