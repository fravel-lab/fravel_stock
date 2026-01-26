import os
import sqlite3
import sys
from os.path import isfile

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants.stock_settings import (CANDLE_PATH, FAVORITE_PATH, STOCK_PATH, STOCK_WATCH_PATH)

if __name__ == "__main__":
    # TODO 2025-02-13 매매관련 DB가 존재하는지 확인하고 없는 경우 새성한다.

    # TODO 2025-02-15 일봉 캔들 저장용 DB
    if not isfile(CANDLE_PATH):
        print(f"{CANDLE_PATH} 테이블이 존재하지 않습니다.")
        print(f"{CANDLE_PATH} 테이블 생성.")
        # TODO 2025-02-13 candle 디비 생성후 테이블 
        conn_candle = sqlite3.connect(CANDLE_PATH) # TODO 2025-02-13 이 시점에 candle.db가 없으면 생성됨
        cur_candle = conn_candle.cursor()
        print("candle_data 테이블 생성")
        cur_candle.execute("CREATE TABLE candle(stock_code text,"
                            " _date text,"
                            " open text,"
                            " high text,"
                            " low text,"
                            " close text,"
                            " changes text,"
                            " volume text,"
                            " tr_price text);")
        conn_candle.commit()
        conn_candle.close()


    # TODO 2025-02-15 1차 정리항목 DB
    if not isfile(STOCK_WATCH_PATH):
        print(f"{STOCK_WATCH_PATH} 테이블이 존재하지 않습니다.")
        print(f"{STOCK_WATCH_PATH} 테이블 생성.")
        # TODO 2025-02-13 candle 디비 생성후 테이블 
        conn_candle = sqlite3.connect(STOCK_WATCH_PATH) # TODO 2025-02-13 이 시점에 stock_watch.db가 없으면 생성됨
        cur_candle = conn_candle.cursor()
        print("stock_watch 테이블 생성")
        cur_candle.execute("CREATE TABLE stock_watch(stock_code text, stock_name text);")
        conn_candle.commit()
        conn_candle.close()

