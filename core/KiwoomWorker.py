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
from pprint import pprint
from constants.stock_settings import API_ID, API_URL, CANDLE_PATH, CODE_TO_STOCK_PATH, MOCK_API_URL, RESPONSE_DICT, STOCK_PATH, STOCK_TO_CODE_PATH, TR_DICT
import pandas as pd
from queue import Queue as ThreadQueue

from core.WebSocketWorker import WebSocketWorker


app = QtWidgets.QApplication(sys.argv)


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
        self.teleQ = _qlist[3]
        
        self.ws_worker = None
        self.ws_sendQ = None
        self.ws_recvQ = None
        
        # TODO 2024-08-18 피클 데이터 초기화
        if len(self.code_to_stock) == 0:
            with open(CODE_TO_STOCK_PATH, "rb") as f:
                self.code_to_stock = pickle.load(f)
            with open(STOCK_TO_CODE_PATH, "rb") as f:
                self.stock_to_code = pickle.load(f)
            print(f'code_to_stock length : {len(self.code_to_stock)}')
        
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
        response = requests.post(token_url, headers=headers, json=params)
        
        # print('Code:', response.status_code)
        # print('Header:', json.dumps({key: response.headers.get(key) for key in ['next-key', 'cont-yn', 'api-id']}, indent=4, ensure_ascii=False))
        
        return_code = response.json()['return_code']
        return_msg = response.json()['return_msg']
        
        if (return_code != 0):
            self.windowQ.put([RESPONSE_DICT["로그텍스트"], f"토큰 요청 실패 - {return_msg}"])
            return
        
        return response.json()['token']
    
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
            if self.settings.value("trading_type", "mock") == "mock":
                account_url = f"{MOCK_API_URL}/api/dostk/acnt"
            else:
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
            self.windowQ.put([RESPONSE_DICT["계좌정보"], response.json()])
            # self.windowQ.put([RESPONSE_DICT["로그텍스트"], f"계좌정보 수신 완료"])
        else:
            self.windowQ.put([RESPONSE_DICT["로그텍스트"], "API 토큰이 없습니다."])
    
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
                self.windowQ.put([RESPONSE_DICT["로그텍스트2"], f"코스피 종목정보 수신 완료 - {len(stock_list)}건"])
            elif market_type == '10':
                print(f"코스닥 종목정보 수신 완료 - {len(stock_list)}건")
                self.windowQ.put([RESPONSE_DICT["로그텍스트2"], f"코스닥 종목정보 수신 완료 - {len(stock_list)}건"])
            
            # TODO 2026-01-23 Loop를 돌면서 실행하므로 코스피인 경우에만 실행하도록 수정(코스닥도 체크하면 계송 중복으로 생성됨)
            if isfile(STOCK_PATH) and market_type == '0':
                print("디비 파일 재생성 :"+ market_type)
                self.windowQ.put([RESPONSE_DICT['로그텍스트2'], "디비 파일 재생성"])
                # TODO 2024-11-26 기존 파일은 삭제하지 않고 stock(Ymd).db 파일로 변경
                if isfile(STOCK_PATH.replace(".db", f"({self.today}).db")):
                    self.windowQ.put([RESPONSE_DICT['로그텍스트2'], "디비 파일 재생성 - 기존 파일 있음"])
                    # TODO 2024-11-26 YMD 파일명이 있을 경우 ymd_1, ymd_2 순으로 숫자를 올리면서 rename한다.
                    tmp_i = 1
                    while isfile(STOCK_PATH.replace(".db", f"({self.today}_{tmp_i}).db")):
                        tmp_i += 1
                    rename(STOCK_PATH, STOCK_PATH.replace(".db", f"({self.today}_{tmp_i}).db"))
                else:
                    # TODO 2024-11-26 YMD 파일명이 없을 경우 YMD.db로 생성
                    self.windowQ.put([RESPONSE_DICT['로그텍스트2'], "디비 파일 재생성 - 기존 파일 없음"])
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
                
                self.windowQ.put([RESPONSE_DICT["로그텍스트2"], "pickle데이터 저장 완료"])
        
        self.windowQ.put([RESPONSE_DICT["로그텍스트2"], "종목정보 수신 완료"])
        
    def download_candle(self, candle_ymd):
        if isfile(STOCK_PATH):
            conn_stock = sqlite3.connect(STOCK_PATH)
        else:
            self.windowQ.put([RESPONSE_DICT["로그텍스트2"], "stock.db 파일이 없습니다."])
            return
        
        cur_stock = conn_stock.cursor()
        
        # TODO 2026-01-24 전체 주식의 code를 구한다.
        stock_codes = cur_stock.execute("SELECT code FROM market_data;").fetchall()
        
        for index, stock_code in enumerate(stock_codes):
            # TODO 2026-01-26 특정 index 이후로 다운받으려면 아래 코드 실행
            if index < 1695: # 해당 종목의 index-1
                continue
            stock_code = stock_code[0] # 종목 코드명
            print(f"{self.code_to_stock[stock_code]} 일봉 다운로드 시작 - {index + 1} / {len(stock_codes)}")
            self.windowQ.put([RESPONSE_DICT["로그텍스트2"], f"{self.code_to_stock[stock_code]} 일봉 다운로드 시작 - {index + 1} / {len(stock_codes)}"])
            con_candle = sqlite3.connect(CANDLE_PATH)
            cur_candle = con_candle.cursor()  # DB 연결
        
            # TODO 2026-01-24 일봉 다운로드
            candle_url = f"{API_URL}/api/dostk/chart"

            headers = {
                'Content-Type': 'application/json;charset=UTF-8',
                'authorization': f'Bearer {self.settings.value("api_token", "")}',
                'next-key': '',
                'api-id': API_ID["일봉차트조회"],
            }
            params = {
                'stk_cd': stock_code,
                'base_dt': candle_ymd,
                'upd_stkpc_tp': '1', # 수정주가구분 0 or 1
            }

            response = requests.post(candle_url, headers=headers, json=params)
            return_code = response.json()['return_code']
            return_msg = response.json()['return_msg']
            
            # print('Header:', json.dumps({key: response.headers.get(key) for key in ['next-key', 'cont-yn', 'api-id']}, indent=4, ensure_ascii=False))
            # print('Body:', json.dumps(response.json(), indent=4, ensure_ascii=False))  # JSON 응답을 파싱하여 출력
            print(f"첫 번째 응답 - {len(response.json()['stk_dt_pole_chart_qry'])}건")
            
            if (return_code != 0):
                self.windowQ.put([RESPONSE_DICT["로그텍스트2"], f"일별주가요청 실패 - {return_code} {return_msg}"])
                
            # TODO 2026-01-24 header 응답의 cont-yn이 Y이고 next-key가 있을 경우 연속조회 요청
            stock_data = []
            stock_data.extend(response.json()['stk_dt_pole_chart_qry'])
            cont_cnt = 1
            while response.headers.get('cont-yn') == 'Y' :
                next_key = response.headers.get('next-key')
                if not next_key:
                    return
                
                headers = {
                    'Content-Type': 'application/json;charset=UTF-8',
                    'authorization': f'Bearer {self.settings.value("api_token", "")}',
                    'next-key': next_key,
                    'api-id': API_ID["일봉차트조회"],
                }
                
                last_item = response.json()['stk_dt_pole_chart_qry'][-1]
                
                continue_candle_ymd = last_item['dt']
                
                print(f"연속조회 일자 - {candle_ymd}")
                params = {
                    'stk_cd': stock_code,
                    'base_dt': continue_candle_ymd,
                    'upd_stkpc_tp': '1', # 수정주가구분 0 or 1
                }
                
                response = requests.post(candle_url, headers=headers, json=params)
                print(f"연속조회 응답 - {len(response.json()['stk_dt_pole_chart_qry'])}건")
                # print('Body:', json.dumps(response.json(), indent=4, ensure_ascii=False))  # JSON 응답을 파싱하여 출력
                stock_data.extend(response.json()['stk_dt_pole_chart_qry'])
                sleep(.2)
                cont_cnt += 1
                
                # TODO 2026-01-27 연속조회 최대 5번 시도
                if cont_cnt > 5:
                    break
                
            # TODO 2026-01-24 'dt' 컬럼으로 중복 제거
            df = pd.DataFrame(stock_data)
            df = df.drop_duplicates(subset=['dt'])
            duplicate_count = len(stock_data) - len(df)
            print(f"중복 제거된 건수: {duplicate_count}")
            print(f"{self.code_to_stock[stock_code]} 일봉 다운로드 완료 - {len(df)}건")
            
            # TODO 2026-01-24 candle.db 에 저장
            for index, row in df.iterrows():
                # 종목, 날짜, 시가, 고가, 저가, 종가, 전일대비, 거래량, 거래대금
                cur_candle.execute("INSERT INTO candle VALUES (?,?,?,?,?,?,?,?,?)", (stock_code, row['dt'], row['open_pric'], row['high_pric'], row['low_pric'], row['cur_prc'], row['pred_pre'], row['trde_qty'], row['trde_prica']))
            
            print(f"{self.code_to_stock[stock_code]} 일봉 저장 완료")
            self.windowQ.put([RESPONSE_DICT["로그텍스트2"], f"{self.code_to_stock[stock_code]} 일봉 저장 완료"])
            con_candle.commit()

            cur_candle.close()
            con_candle.close()
            
            sleep(3)
        
        cur_stock.close()
        conn_stock.close()
            
    def start_websocket(self, api_token):
        self.windowQ.put([RESPONSE_DICT["로그텍스트"], "WebSocket 시작"])
        self.ws_sendQ = ThreadQueue()
        self.ws_recvQ = ThreadQueue()
        
        self.ws_worker = WebSocketWorker(
            token=api_token,
            sendQ=self.ws_sendQ,
            recvQ=self.ws_recvQ,
            windowQ=self.windowQ,
        )
        
        self.ws_worker.daemon = True
        self.ws_worker.start()
        
    def EventLoop(self):
        while True:
            if self.ws_recvQ is not None and self.ws_worker is not None:
                # while not self.ws_recvQ.empty() and self.ws_worker.is_alive():
                while not self.ws_recvQ.empty():
                    print("WS 수신 루프 실행")
                    data = self.ws_recvQ.get()
                    trnm = data.get("trnm")
                    
                    # self.windowQ.put([RESPONSE_DICT["로그텍스트"], f"WS Receive - {trnm} : {data}"])

                    if trnm == TR_DICT["조건검색목록"]: # CNSRLST
                        self.windowQ.put([RESPONSE_DICT["조건검색목록 결과"], data])
                    elif trnm == TR_DICT["조건검색 요청 실시간"]: # CNSRREQ
                        self.windowQ.put([RESPONSE_DICT["조건검색 요청 결과"], data])
                    else:
                        self.windowQ.put([RESPONSE_DICT["로그텍스트"], f"미처리 WS 데이터: {data}"])
                    
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
                    
                    self.windowQ.put([RESPONSE_DICT["로그텍스트"], f"실전 API 토큰 수신 완료 - {api_token}"])
                    self.windowQ.put([RESPONSE_DICT["로그텍스트"], f"모의투자 API 토큰 수신 완료 - {mock_api_token}"])
                    self.windowQ.put([RESPONSE_DICT["API_TOKEN"], api_token])
                    self.windowQ.put([RESPONSE_DICT["MOCK_API_TOKEN"], mock_api_token])
                    
                    # TODO 2026-01-24 텔레그램 메시지 발송 주석 처리(임시)
                    # self.teleQ.put(f"API_TOKEN - {api_token}")
                    # self.teleQ.put(f"MOCK_API_TOKEN - {mock_api_token}")

                elif event[0] == "account_info":
                    self.get_account_info()
                    
                elif event[0] == "market_data":
                    self.download_market_data()
                    
                elif event[0] == "candle_save":
                    # TODO 2026-01-24 일봉 저장
                    self.candle_range = event[1]  # 이벤트 타입 정의(전체기간, 일부기간)
                    self.candle_ymd = event[2]  # 기준일자는 키움증권에 필요
                    self.candle_provider = event[3] # 일봉 제공자(야후파이낸스, 키움증권)
                    
                    print(f"candle_save - {self.candle_range}, {self.candle_ymd}, {self.candle_provider}")
                    self.download_candle(self.candle_ymd)
                    
                elif event[0] == "start_websocket": # TODO 2026-01-27 웹소켓 스레드 시작
                    print("웹소켓 스레드 시작")
                    
                    if self.settings.value("trading_type", "mock") == "mock":
                        api_token = self.settings.value("mock_api_token", "")
                    else:
                        api_token = self.settings.value("api_token", "")
                    
                    if not api_token:
                        self.windowQ.put([RESPONSE_DICT["로그텍스트"], "WebSocket 시작 실패: API 토큰 없음"])
                        return
                    
                    self.start_websocket(api_token)
                
                elif event[0] == "stop_websocket": # TODO 2026-01-27 웹소켓 스레드 종료
                    if self.ws_worker:
                        self.ws_worker.stop()
                        self.ws_worker = None
                        self.windowQ.put([RESPONSE_DICT["로그텍스트"], "WebSocket 스레드 종료"])
                        
                elif event[0] == "condition_load": # TODO 2026-01-27 조건식 로드
                    if not self.ws_worker or not self.ws_worker.is_alive():
                        self.windowQ.put(["LOG", "WebSocket 미연결"])
                        return

                    cmd = {
                        "trnm": TR_DICT["조건검색목록"], # CNSRLST
                    }

                    self.ws_sendQ.put(cmd)
                
                elif event[0] == "condition_detail": # TODO 2026-01-27 조건식 세부 종목 로드
                    if not self.ws_worker or not self.ws_worker.is_alive():
                        self.windowQ.put(["LOG", "WebSocket 미연결"])
                        return
                    
                    # TODO 2026-01-27 조건식 세부 종목 요청
                    condition_index = event[1]
                    # 실시간 검색 방식(추후 사용 예정)
                    # cmd = {
                    #     "trnm": TR_DICT["조건검색 요청 실시간"], # CNSRLST
                    #     "seq" : condition_index, # 조건검색식 일련번호
                    #     "search_type" : "0", # 1: 조건검색+실시간조건검색
                    #     "stex_tp" : "K" # K:KRX
                    # }
                    
                    # 일반 조건검색 방식(실시간 아님)
                    cmd = {
                        "trnm" : TR_DICT["조건검색 요청 일반"], #
                        "seq" : condition_index, # 조건검색식 일련번호
                        "search_type" : "0", # 0: 일반
                        "stex_tp" : "K",
                        # "cont_yn" : "N", # 필수 아님
                        # "next_key" : "" # 필수 아님
                    }

                    self.ws_sendQ.put(cmd)

            
            time.sleep(0.0001)
            
            