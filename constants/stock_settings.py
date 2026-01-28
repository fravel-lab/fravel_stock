import os
from PyQt5.QtGui import QColor

# TODO 2024-11-12 프로젝트 루트
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# TODO 2024-11-12 데이터 관련 DIR
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_DIR = os.path.join(DATA_DIR, 'db')
TICK_DIR = os.path.join(DATA_DIR, 'tick')
SETTINGS_DIR = os.path.join(BASE_DIR, 'config')

# TODO 2024-11-12 파일 경로
FRAVEL_TRADER_SETTING_PATH = os.path.join(SETTINGS_DIR, 'trader_setting.ini')  # 틱 다운로더 설정
STOCK_PATH = os.path.join(DB_DIR, 'stock.db')  # 주식 종목 정보
STOCK_WATCH_PATH = os.path.join(DB_DIR, 'stock_watch.db')  # 관심종목 종목 정보
FAVORITE_PATH = os.path.join(DB_DIR, 'favorite.db')  # 관심종목 종목 정보
CANDLE_PATH = os.path.join(DB_DIR, 'candle.db')  # 캔들 정보
CODE_TO_STOCK_PATH = os.path.join(DATA_DIR, 'code_to_stock.pickle')  # 종목 코드를 주식 이름으로 변환
STOCK_TO_CODE_PATH = os.path.join(DATA_DIR, 'stock_to_code.pickle')  # 주식 이름을 종목 코드로 변환

# TODO 2024-11-21 
Q_LIST = {
    "로그텍스트": 0,
    "로그텍스트2": 1,
    "로그텍스트3": 2,
    "로그텍스트4": 3,
    "로그텍스트5": 4,
    "계좌정보": 5,
    "주식평가": 6,
    "주식평가_종목별": 7,
    "즐겨찾기": 8,
    "캔들일자": 9,
    "조건식": 11,
    "조건식 종목": 12,
    "틱데이터": 13,
    "즐겨찾기 추가": 14,
    "즐겨찾기 제거": 15,
    "1차 관심종목 리스트": 16,
    "1차 관심종목 추가": 17,
    "1차 관심종목 제거": 18,
    "일자별 주가": 19,
    "틱데이터-1분": 20,
    "API_TOKEN": 21,
    "MOCK_API_TOKEN": 22,
    "조건검색목록 결과": 23,
    "조건검색 요청 결과": 24,
}

API_ID = {
    "계좌정보": "ka01690",
    "종목정보": "ka10099",
    "일봉차트조회": "ka10081",
}

TR_DICT = {
    "조건검색목록": "CNSRLST",
    "조건검색 요청 실시간": "CNSRREQ",
    "조건검색 실시간 해제": "CNSRCLR",
    "조건검색 요청 일반": "CNSRREQ",
}



# TODO 2024-11-21 생략할 계좌 번호
IGNORE_ACCOUNT_LIST = ["3389376621"]
FIRST_ACCOUNT = "3389376611"

# 색깔 정의
COLOR_GRAY = QColor(53, 53, 53) # 기본색(그레이)
COLOR_RED = QColor(255, 65, 129) # 빨간색
COLOR_BLUE = QColor(3, 169, 244) # 파란색
COLOR_WHITE = QColor(255, 255, 255) # 흰색

COLOR_CANDLE_RED = QColor(237, 55, 56) # 빨간색
COLOR_CANDLE_BLUE = QColor(0, 125, 243) # 파란색

BTN_FAV_ON = "rgb(255, 0, 0)"
BTN_FAV_OFF = "rgb(53, 53, 53)"
