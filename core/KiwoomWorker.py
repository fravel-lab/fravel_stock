from os import remove, rename
from os.path import isfile
import pickle
import sqlite3
import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QSettings
import time
import requests
import json
from time import sleep

from constants.stock_settings import API_ID, CODE_TO_STOCK_PATH, Q_LIST, STOCK_PATH, STOCK_TO_CODE_PATH

app = QtWidgets.QApplication(sys.argv)

API_URL = "https://api.kiwoom.com"
MOCK_API_URL = "https://mockapi.kiwoom.com"

class KiwoomWorker:
    today = QDate.currentDate().toString("yy_MM_dd")
    code_to_stock = {}  # code_to_stock 피클 데이터 저장용 리스트
    stock_to_code = {}  # code_to_stock 피클 데이터 저장용 리스트
    receive_cnt = 0
    tick_list = []
    
    settings = QSettings('config/trader_setting.ini', QSettings.IniFormat)
    
    def __init__(self, _qlist):
        # TODO 2024-11-21 데이터프레임 출력 설정
        # pd.set_option('display.max_rows', None)  # 모든 행 출력
        # pd.set_option('display.max_columns', None)  # 모든 열 출력
        # pd.set_option('display.width', None)  # 너비 제한 없음
        # pd.set_option('display.max_colwidth', None)  # 컬럼 너비 제한 없음

        self.eventQ = _qlist[0]
        self.windowQ = _qlist[1]
        self.settingsQ = _qlist[2]
        self.dataQ = _qlist[3]
        self.teleQ = _qlist[4]
        
        self.EventLoop()
        
    def get_token(self, api_url, api_key, api_secret):
        token_url = f"{api_url}/oauth2/token"
        
        print(f"token_url: {token_url}")
        
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
        }
        params = {
            'grant_type': 'client_credentials',
            'appkey': api_key,
            'secretkey': api_secret,
        }
        r = requests.post(token_url, headers=headers, json=params)
        
        return r.json()['token']
    
    def create_header(self, url, api_id):
        # TODO 2026-01-23 헤더 생성 함수(연속조회 안하는 경우만)
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'authorization': f'Bearer {self.settings.value("api_token", "")}',
            'cont-yn': 'N',
            'next-key': '',
            'api-id': api_id,
        }
        return headers

    def get_account_info(self):
        # TODO 2026-01-23 계좌 정보 조회
        if self.settings.value("api_token", "") != "":
            account_url = f"{API_URL}/api/dostk/acnt"
            today = QDate.currentDate().toString("yyyyMMdd")    
            headers = self.create_header(account_url, API_ID["계좌정보"])
            params = {
                'qry_dt': today, # 조회일자 
            }
            
            response = requests.post(account_url, headers=headers, json=params)
            # print('Code:', response.status_code)
            # print('Header:', json.dumps({key: response.headers.get(key) for key in ['next-key', 'cont-yn', 'api-id']}, indent=4, ensure_ascii=False))
            # print('Body:', json.dumps(response.json(), indent=4, ensure_ascii=False))  # JSON 응답을 파싱하여 출력
            self.windowQ.put([Q_LIST["계좌정보"], response.json()])
            self.windowQ.put([Q_LIST["로그텍스트"], f"계좌정보 수신 완료"])
        else:
            self.windowQ.put([Q_LIST["로그텍스트"], "API 토큰이 없습니다."])
    
    def download_market_data(self):
        # TODO 2026-01-23 코스피, 코스닥 종목 데이터 다운로드
        market_data_url = f"{API_URL}/api/dostk/stkinfo"
        headers = self.create_header(market_data_url, API_ID["종목정보"])
        
        market_types = [
            '0', # 코스피
            '10', # 코스닥
        ]
        
        for market_type in market_types:
            params = {  
                'mrkt_tp': market_type, # 시장구분 0 : 코스피, 10: 코스닥
            }
            
            response = requests.post(market_data_url, headers=headers, json=params)

            stock_list = response.json()['list']   
            
            if market_type == '0':
                print(f"코스피 종목정보 수신 완료 - {len(stock_list)}건")
                self.windowQ.put([Q_LIST["로그텍스트2"], f"코스피 종목정보 수신 완료 - {len(stock_list)}건"])
            elif market_type == '10':
                print(f"코스닥 종목정보 수신 완료 - {len(stock_list)}건")
                self.windowQ.put([Q_LIST["로그텍스트2"], f"코스닥 종목정보 수신 완료 - {len(stock_list)}건"])
            
            # TODO 2026-01-23 Loop를 돌면서 실행하므로 코스피인 경우에만 실행하도록 수정(코스닥도 체크하면 계송 중복으로 생성됨)
            if isfile(STOCK_PATH) and market_type == '0':
                print("디비 파일 재생성 :"+ market_type)
                self.windowQ.put([Q_LIST['로그텍스트2'], "디비 파일 재생성"])
                # TODO 2024-11-26 기존 파일은 삭제하지 않고 stock(Ymd).db 파일로 변경
                if isfile(STOCK_PATH.replace(".db", f"({self.today}).db")):
                    self.windowQ.put([Q_LIST['로그텍스트2'], "디비 파일 재생성 - 기존 파일 있음"])
                    # TODO 2024-11-26 YMD 파일명이 있을 경우 ymd_1, ymd_2 순으로 숫자를 올리면서 rename한다.
                    tmp_i = 1
                    while isfile(STOCK_PATH.replace(".db", f"({self.today}_{tmp_i}).db")):
                        tmp_i += 1
                    rename(STOCK_PATH, STOCK_PATH.replace(".db", f"({self.today}_{tmp_i}).db"))
                else:
                    # TODO 2024-11-26 YMD 파일명이 없을 경우 YMD.db로 생성
                    self.windowQ.put([Q_LIST['로그텍스트2'], "디비 파일 재생성 - 기존 파일 없음"])
                    rename(STOCK_PATH, STOCK_PATH.replace(".db", f"({self.today}).db"))
                
                # TODO 2026-01-23 pickle데이터 삭제
                if isfile(CODE_TO_STOCK_PATH):
                    remove(CODE_TO_STOCK_PATH)
                if isfile(STOCK_TO_CODE_PATH):
                    remove(STOCK_TO_CODE_PATH)
            
            # 2020-06-20 DB생성
            con_stock = sqlite3.connect(STOCK_PATH)
            cur_stock = con_stock.cursor()  # DB 연결

            # 테이블 존재유무 확인(구조 : [(0,)])
            check_table = "SELECT COUNT(*) FROM sqlite_master WHERE name='market_data';"
            
            if cur_stock.execute(check_table).fetchone()[0] == 0:
                print("stock.db 생성")
                cur_stock.execute("CREATE TABLE market_data(code text, stock_name text, market_type text);")
            else:
                print("stock.db 존재")

            for stock in stock_list:
                # stock['marketName'] 이 코스닥, 거래소 인 경우만 입력
                if stock['marketName'] == "코스닥" or stock['marketName'] == "거래소":
                    cur_stock.execute("INSERT INTO market_data Values (?,?,?)", (stock['code'], stock['name'], stock['marketName']))
                    # TODO 2026-01-23 pickle데이터 생성
                    self.code_to_stock[stock['code']] = stock['name']
                    self.stock_to_code[stock['name']] = stock['code']
                    
            con_stock.commit()
            con_stock.close()
            
            # TODO 2026-01-23 마지막 요청시 pickle데이터는 저장(코스닥인 경우)
            if market_type == '10':
                with open(CODE_TO_STOCK_PATH, 'wb') as f:
                    pickle.dump(self.code_to_stock, f)
                with open(STOCK_TO_CODE_PATH, 'wb') as f:
                    pickle.dump(self.stock_to_code, f)
                
                self.windowQ.put([Q_LIST["로그텍스트2"], "pickle데이터 저장 완료"])
        
        self.windowQ.put([Q_LIST["로그텍스트2"], "종목정보 수신 완료"])

    def EventLoop(self):
        while True:
            if not self.eventQ.empty():
                event = self.eventQ.get()
                
                if event[0] == "reload_token":
                    print("reload_token")
                    api_key = self.settings.value("app_key", "")
                    api_secret = self.settings.value("secret_key", "")
                    mock_api_key = self.settings.value("mock_app_key", "")
                    mock_api_secret = self.settings.value("mock_secret_key", "")
                    
                    api_token = self.get_token(API_URL, api_key, api_secret)
                    mock_api_token = self.get_token(MOCK_API_URL, mock_api_key, mock_api_secret)
                    
                    self.windowQ.put([Q_LIST["로그텍스트"], f"실전 API 토큰 수신 완료 - {api_token}"])
                    self.windowQ.put([Q_LIST["로그텍스트"], f"모의투자 API 토큰 수신 완료 - {mock_api_token}"])
                    self.windowQ.put([Q_LIST["API_TOKEN"], api_token])
                    self.windowQ.put([Q_LIST["MOCK_API_TOKEN"], mock_api_token])
                    
                    self.teleQ.put(f"API_TOKEN - {api_token}")
                    self.teleQ.put(f"MOCK_API_TOKEN - {mock_api_token}")

                elif event[0] == "account_info":
                    self.get_account_info()
                    
                elif event[0] == "market_data":
                    self.download_market_data()
                    
            time.sleep(0.0001)
            
            