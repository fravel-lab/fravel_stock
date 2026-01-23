import requests
import json

# 종목정보 리스트
def fn_ka10099(token, data, cont_yn='N', next_key=''):
	# 1. 요청할 API URL
	#host = 'https://mockapi.kiwoom.com' # 모의투자
	host = 'https://api.kiwoom.com' # 실전투자
	endpoint = '/api/dostk/stkinfo'
	url =  host + endpoint

	# 2. header 데이터
	headers = {
		'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
		'authorization': f'Bearer {token}', # 접근토큰
		'cont-yn': cont_yn, # 연속조회여부
		'next-key': next_key, # 연속조회키
		'api-id': 'ka10099', # TR명
	}

	# 3. http POST 요청
	response = requests.post(url, headers=headers, json=data)

	# 4. 응답 상태 코드와 데이터 출력
	print('Code:', response.status_code)
	print('Header:', json.dumps({key: response.headers.get(key) for key in ['next-key', 'cont-yn', 'api-id']}, indent=4, ensure_ascii=False))
	# print('Body:', json.dumps(response.json(), indent=4, ensure_ascii=False))  # JSON 응답을 파싱하여 출력
	print('Body:', len(response.json()['list']))  # JSON 응답을 파싱하여 출력

# 실행 구간
if __name__ == '__main__':
	# 1. 토큰 설정
	MY_ACCESS_TOKEN = '2SS-2IuLmE51zPZpC_voiUqJpAiU5GjLGpYGW5bBEprnWuwYw868LtoDkv-KBkiNX4wuNsMBOA2unDB2ccrMzg' # 접근토큰

	# 2. 요청 데이터
	params = {
		'mrkt_tp': '10', # 시장구분 0 : 코스피,
# 10 : 코스닥,
# 30 : K-OTC,
# 50 : 코넥스,
# 60 : ETN,
# 70 : 손실제한 ETN,
# 80 : 금현물,
# 90 : 변동성 ETN,
# 2 : 인프라투융자,
# 3 : ELW,
# 4 : 뮤추얼펀드,
# 5 : 신주인수권,
# 6 : 리츠종목,
# 7 : 신주인수권증서,
# 8 : ETF,
# 9 : 하이일드펀드
	}

	# 3. API 실행
	fn_ka10099(token=MY_ACCESS_TOKEN, data=params)

	# next-key, cont-yn 값이 있을 경우
	# fn_ka10099(token=MY_ACCESS_TOKEN, data=params, cont_yn='Y', next_key='nextkey..')