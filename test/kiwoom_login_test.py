import requests
import json
from pprint import pprint
from datetime import datetime

# URL = "https://mockapi.kiwoom.com"
URL = "https://api.kiwoom.com"
APP_KEY = "rwJudnLsQWWjQ819m1fje4HliYh6Cht3rqj7CSpTyaY"
APP_SECRET = "UgfoibJDph2uJXeUJ7XMGmMc4sNKnEe-8pRJZ0EKvTA"
TOKEN = "9R20hI1yvYiMmm6wilf0KRzyQ2Jk_S9AKWtgPYSYQ6XwJ9sVRS76ckuxsCBfeKu2cxf_h3CrXzxoLvFZ6zeUmA"

# 일별잔고수익률
def fn_ka01690(token, data, cont_yn='N', next_key=''):
	# 1. 요청할 API URL
	host = 'https://mockapi.kiwoom.com' # 모의투자
	# host = 'https://api.kiwoom.com' # 실전투자
	endpoint = '/api/dostk/acnt'
	url =  host + endpoint

	# 2. header 데이터
	headers = {
		'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
		'authorization': f'Bearer {token}', # 접근토큰
		'cont-yn': cont_yn, # 연속조회여부
		'next-key': next_key, # 연속조회키
		'api-id': 'ka01690', # TR명
	}

	# 3. http POST 요청
	response = requests.post(url, headers=headers, json=data)

	# 4. 응답 상태 코드와 데이터 출력
	print('Code:', response.status_code)
	print('Header:', json.dumps({key: response.headers.get(key) for key in ['next-key', 'cont-yn', 'api-id']}, indent=4, ensure_ascii=False))
	print('Body:', json.dumps(response.json(), indent=4, ensure_ascii=False))  # JSON 응답을 파싱하여 출력


def get_token():
    token_url = f"{URL}/oauth2/token"
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
    }
    params = {
        'grant_type': 'client_credentials',
        'appkey': APP_KEY,
        'secretkey': APP_SECRET,
    }
    r = requests.post(token_url, headers=headers, json=params)
    print(r.json())

# 실행 구간
if __name__ == '__main__':
    
    get_token()
	# 1. 토큰 설정
	# MY_ACCESS_TOKEN = '사용자 AccessToken' # 접근토큰

	# 2. 요청 데이터
	# params = {
	# 	'qry_dt': '20260113', # 조회일자 
	# }

	# # 3. API 실행
	# fn_ka01690(token=TOKEN, data=params)

	# next-key, cont-yn 값이 있을 경우
	# fn_ka01690(token=MY_ACCESS_TOKEN, data=params, cont_yn='Y', next_key='nextkey..')