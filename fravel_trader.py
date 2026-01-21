__main__ = "__main__"

from multiprocessing import Queue
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QSettings
from constants.stock_settings import (FRAVEL_TRADER_SETTING_PATH, BASE_DIR, DATA_DIR, DB_DIR, TICK_DIR, SETTINGS_DIR, FAVORITE_PATH, CANDLE_PATH, CODE_TO_STOCK_PATH, STOCK_TO_CODE_PATH, STOCK_PATH)

from ui.fravel_trader_ui import Ui_MainWindow
import sys
from PyQt5.QtCore import QDate
from util.FravelUtils import set_dark_theme

from PyQt5.QtGui import QIntValidator

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(FRAVEL_TRADER_SETTING_PATH, QSettings.IniFormat)
        self.ui = Ui_MainWindow()
        
        self.candle_provider = self.settings.value("candle_provider", "kiwoom")  # 기본값은 kiwoom으로 설정
        self.today = QDate.currentDate().toString("yy_MM_dd")
        
        # TODO 2024-11-13 클래스 변수 선언
        self.account = ''
        self.candle_latest_date = '' # TODO 2024-12-04 candle.db의 최신 날짜
        self.current_stock_name = ''
        
        self.ui.setupUi(self)
        self.resize(2300, 1500)
        
        self.init_UI()
        
    def init_UI(self):
        set_dark_theme()
        
        # TODO 2025-02-04 사이보스 상태 설정
        if sys.platform == 'win32':
            self.cybos = win32com.client.Dispatch("CpUtil.CpCybos")
            value = self.cybos.IsConnect
            if value == 0:
                print("사이보스 로그인 실패")
                self.ui.label_cybos_status.setText("사이보스 : 로그아웃")
                eventQ.put(["cybos_login", False])
            else:
                print("사이보스 로그인 성공")
                self.ui.label_cybos_status.setText("사이보스 : 로그인")
                eventQ.put(["cybos_login", True])


        # 2021-04-01 UI 기본 값 설정
        self.ui.text_path.setText(self.settings.value("path", "c:/_db"))
        self.ui.btn_delete_candle.clicked.connect(self.delete_candle)
        self.ui.btn_save_candle.clicked.connect(self.get_candle)
        self.ui.btn_delete_save_candle.clicked.connect(self.delete_save_candle)
        
        
        self.ui.btn_tick_down.clicked.connect(self.set_real_reg_all)  # 2022-11-30 틱 다운로드 시작
        self.ui.btn_save_now.clicked.connect(self.get_tick_now)  # 2022-11-30 현재 틱 즉시 다운로드
        self.ui.btn_stock_down.clicked.connect(self.get_market_data)
        self.ui.btn_path_set.clicked.connect(self.set_path)
        self.ui.btn_default.clicked.connect(self.set_default_path)
        self.ui.btn_path_open.clicked.connect(self.path_open)
        self.ui.btn_reset.clicked.connect(self.reset_output)
        self.ui.btn_ohlcv.clicked.connect(self.load_ohlcv)
        self.ui.btn_login.clicked.connect(self.login_kiwoom)  # 2024-08-29 로그인 버튼
        self.ui.btn_load_condition.clicked.connect(self.load_condition)
        self.ui.list_condition.itemClicked.connect(self.load_condition_detail)
        
        self.ui.table_balance.setColumnWidth(2, 80) # 손익금액
        self.ui.table_balance.setColumnWidth(3, 70) # 수익률

        # 기본 전체종목 테이블
        self.ui.table_stock_list.setColumnWidth(0, 180)
        self.ui.table_stock_list.setColumnWidth(1, 80)
        self.ui.table_stock_list.setColumnWidth(2, 80)
        self.ui.table_stock_list.setColumnWidth(3, 70)
        self.ui.table_stock_list.setColumnWidth(4, 70)
        self.ui.table_stock_list.setColumnWidth(5, 70)
        self.ui.table_stock_list.setColumnWidth(6, 70)
        self.ui.table_stock_list.setColumnWidth(7, 90)
        self.ui.table_stock_list.setAlternatingRowColors(True)
        
        # 1차 관심종목 테이블
        self.ui.table_stock_watch.setColumnWidth(0, 180)
        self.ui.table_stock_watch.setColumnWidth(1, 80)
        self.ui.table_stock_watch.setColumnWidth(2, 80)
        self.ui.table_stock_watch.setColumnWidth(3, 70)
        self.ui.table_stock_watch.setColumnWidth(4, 70)
        self.ui.table_stock_watch.setColumnWidth(5, 70)
        self.ui.table_stock_watch.setColumnWidth(6, 70)
        self.ui.table_stock_watch.setColumnWidth(7, 60)
        self.ui.table_stock_watch.setColumnWidth(8, 90)
        self.ui.table_stock_watch.setAlternatingRowColors(True)
        
        # 즐겨찾기 종목 테이블
        self.ui.table_favorite.setColumnWidth(0, 160) # 종목명
        self.ui.table_favorite.setColumnWidth(1, 70) # 종목코드
        self.ui.table_favorite.setColumnWidth(2, 70) # 구분
        self.ui.table_favorite.setColumnWidth(3, 70) # 시가
        self.ui.table_favorite.setColumnWidth(4, 70) # 고가
        self.ui.table_favorite.setColumnWidth(5, 75) # 저가
        self.ui.table_favorite.setColumnWidth(6, 85) # 종가
        self.ui.table_favorite.setColumnWidth(7, 70) # 등락률
        self.ui.table_favorite.setColumnWidth(8, 90) # 거래량
        self.ui.table_favorite.setColumnWidth(9, 70) # 일봉
        self.ui.table_favorite.setAlternatingRowColors(True)
        
        # 일봉 테이블 세팅
        self.ui.table_stock_ohlcv.setAlternatingRowColors(True)
        self.ui.table_stock_ohlcv.setSortingEnabled(True) # TODO 2025-02-14  정렬기능 사용
        self.ui.table_stock_ohlcv.setColumnWidth(1, 80) # 시가 
        self.ui.table_stock_ohlcv.setColumnWidth(2, 80) # 고가
        self.ui.table_stock_ohlcv.setColumnWidth(3, 80) # 저가
        self.ui.table_stock_ohlcv.setColumnWidth(4, 80) # 종가
        self.ui.table_stock_ohlcv.setColumnWidth(5, 90) # 거래량
        
        self.ui.table_condition_stock.setColumnWidth(0, 160) # 종목명
        self.ui.table_condition_stock.setColumnWidth(1, 90) # 현재가
        self.ui.table_condition_stock.setColumnWidth(2, 90) # 대비
        # self.ui.table_condition_stock.setColumnWidth(3, 70) # 등락률
        
        self.ui.text_candle_db_path.setText("./data/db/candle.db")
        self.ui.text_candle_db_path.setReadOnly(True) # 읽기 전용

        # TODO 2024-11-13 계좌 콤보박스 초기화
        self.ui.combo_account.currentIndexChanged.connect(self.account_changed)

        # TODO 2024-08-29 탭 사이드 텍스트(탭 우측 사이드에 텍스트 출력해줌)
        # tmpLabel = QLabel(f"최종 업데이트 : {self.candle_latest_date}")
        # container_widget = QWidget()
        # # container_widget.setStyleSheet("background-color: red;")
        # layout = QHBoxLayout(container_widget)
        # layout.addStretch()  # Add stretch to push the label to the right
        # layout.addWidget(tmpLabel)
        # layout.setContentsMargins(0, 0, 0, 5)  # Left, Top, Right, Bottom

        # self.ui.tabWidget.setCornerWidget(container_widget, Qt.TopRightCorner)

        self.today = QDate.currentDate().toString("yyyyMMdd")
        # self.ui.text_ymd.setText(today)

        # TODO 2024-08-19 탭 위치 왼쪽
        # self.ui.tabWidget.setTabPosition(QTabWidget.West)
        
        # TODO 2024-12-23 일봉 수집 방법 선택(야후 파이낸스, 키움증권)
        if self.candle_provider == "kiwoom":
            self.settings.setValue("candle_provider", "kiwoom")
            self.ui.radio_kiwoom.setChecked(True)
        elif self.candle_provider == "cybos":
            self.settings.setValue("candle_provider", "cybos")
            self.ui.radio_cybos.setChecked(True)
        else :
            self.ui.radio_kiwoom.setChecked(True)
            
        # TODO 2024-12-23 람다함수로 setting.ini 업데이트
        self.ui.radio_kiwoom.clicked.connect(lambda: self.settings.setValue("candle_provider", "kiwoom"))
        self.ui.radio_cybos.clicked.connect(lambda: self.settings.setValue("candle_provider", "cybos"))
        
        # TODO 2025-02-07 세팅 탭 초기화
        base_dir = BASE_DIR.replace('\\', '/')
        data_dir = DATA_DIR.replace('\\', '/')
        db_dir = DB_DIR.replace('\\', '/')
        tick_dir = TICK_DIR.replace('\\', '/')
        setting_dir = SETTINGS_DIR.replace('\\', '/')
        setting_path = FRAVEL_TRADER_SETTING_PATH.replace('\\', '/')
        stock_path = STOCK_PATH.replace('\\', '/')
        favorite_path = FAVORITE_PATH.replace('\\', '/')
        candle_path = CANDLE_PATH.replace('\\', '/')
        code_to_stock_path = CODE_TO_STOCK_PATH.replace('\\', '/')
        stock_to_code_path = STOCK_TO_CODE_PATH.replace('\\', '/')
        
        self.ui.text_base_dir.setText(f"{base_dir.replace('e:/OneDrive/fravel_python/', '/')}")
        self.ui.text_data_dir.setText(f"{data_dir.replace('e:/OneDrive/fravel_python/', '/')}")
        self.ui.text_db_dir.setText(f"{db_dir.replace('e:/OneDrive/fravel_python/', '/')}")
        self.ui.text_tick_dir.setText(f"{tick_dir.replace('e:/OneDrive/fravel_python/', '/')}")
        self.ui.text_setting_dir.setText(f"{setting_dir.replace('e:/OneDrive/fravel_python/', '/')}")
        self.ui.text_setting_path.setText(f"{setting_path.replace('e:/OneDrive/fravel_python/', '/')}") 
        self.ui.text_stock_path.setText(f"{stock_path.replace('e:/OneDrive/fravel_python/', '/')}")
        self.ui.text_favorite_path.setText(f"{favorite_path.replace('e:/OneDrive/fravel_python/', '/')}")
        self.ui.text_candle_path.setText(f"{candle_path.replace('e:/OneDrive/fravel_python/', '/')}")
        self.ui.text_code_to_stock_path.setText(f"{code_to_stock_path.replace('e:/OneDrive/fravel_python/', '/')}")
        self.ui.text_stock_to_code_path.setText(f"{stock_to_code_path.replace('e:/OneDrive/fravel_python/', '/')}")
        
        # TODO 2025-02-10 일봉 저장기간 설정
        self.ui.text_candle_range.setText(self.settings.value("candle_day_range", "7"))
        self.ui.text_candle_range.setValidator(QIntValidator(1, 9999)) # 숫자만 입력
        self.ui.text_candle_range.textChanged.connect(lambda: self.settings.setValue("candle_day_range", self.ui.text_candle_range.text()))
        
        # TODO 2025-02-12 일자별 주가 기간 설정(기본 120일)
        self.ui.text_stock_price_range.setText(self.settings.value("stock_price_range", "120"))
        self.ui.text_stock_price_range.setValidator(QIntValidator(1, 9999)) # 숫자만 입력
        self.ui.text_stock_price_range.textChanged.connect(lambda: self.settings.setValue("stock_price_range", self.ui.text_stock_price_range.text())) # .ini 업데이트
        
        # TODO 2025-02-12 ui.table_stock_list, ui.table_stock_watch 클릭 이벤트 설정
        self.ui.table_stock_list.itemClicked.connect(self.stock_list_item_clicked)
        self.ui.table_stock_watch.itemClicked.connect(self.stock_list_item_clicked)
        
        # TODO 2025-02-25 일자별 주가 클릭 이벤트 설정(틱정보 바차트 생성용)
        self.ui.table_stock_ohlcv.itemClicked.connect(self.stock_ohlcv_item_clicked)
        self.ui.table_stock_ohlcv.itemSelectionChanged.connect(self.stock_ohlcv_item_clicked)
    
    def delete_candle(self):
        # TODO 2025-02-12 일봉 삭제(기본 7일)
        reply = QMessageBox.question(self, '확인', f'{self.settings.value("candle_day_range", "7")}일 일봉 데이터를 삭제하시겠습니까?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        else :
            eventQ.put(["candle_delete", self.settings.value("candle_day_range", "7")])

    def get_candle(self):
        # TODO 2025-02-10 전체, 최신 일봉 => 기간 설정으로 변경 (전체 다운로드는 별도 쿼리로 처리하는게 나을듯..)
        eventQ.put(["candle_save", self.settings.value("candle_day_range", "7"), self.today, self.candle_provider, 'save']) # 저장
    
    def delete_save_candle(self):
        # TODO 2025-02-12 저장된 일봉 삭제 후 다운로드
        eventQ.put(["candle_save", self.settings.value("candle_day_range", "7"), self.today, self.candle_provider, 'delete_save']) # 삭제 후 저장
    
    def set_real_reg_all(self):
        # 2022-11-30 틱 다운로드 요청
        # windowQ.put("틱 다운로드 - 요청")
        self.ui.text_ouput.append("틱 다운로드 - 요청")
        # eventQ.put(["tick_download", "default"])
        
    def get_tick_now(self):
        # 2022-11-30 틱 즉시 다운로드
        # windowQ.put("틱 즉시 다운로드 - 요청")
        self.ui.text_ouput.append("틱 즉시 다운로드 - 요청")
        # eventQ.put(["tick_download", "now"])
    
    def get_market_data(self):
        # 2022-11-29 코스피, 코스닥 데이터 갱신
        # windowQ.put("마켓 데이터 - 요청")
        # QMessageBox.warning(self, "알림", "get_market_data 메서드 주석 해제 필요!")
        self.ui.text_ouput.append("마켓 데이터 - 요청")
        eventQ.put(["market_data"])
    
    def set_path(self):
        tmp_dir = self.settings.value("path", "C:/_db")

        # 2021-04-01 기존에 저장된 디렉토리를 오픈한다.
        dir_name = QFileDialog.getExistingDirectory(self, "Select Directory", tmp_dir)

        # 2021-04-01 dir 선택시에만 패스경로를 업데이트한다.
        if dir_name:
            self.ui.text_path.setText(dir_name)
            self.settings.setValue("path", dir_name)
            print("path 선택")
            # 2021-04-01 패스가 변경되면 dir + today 디렉토리를 생성한다.
            create_dir(self.settings.value("path", "C:/_db") + "/" + self.today)
            create_dir(self.settings.value("path", "C:/_db") + "/" + self.today + "/hoga")
            create_dir(self.settings.value("path", "C:/_db") + "/" + self.today + "/stick")
        else:
            print("path 없음")

        self.set_settings()
    
    def load_condition(self):
        # TODO 2024-12-06 조건식 로드
        self.ui.text_ouput.append("조건식 로드 - 요청")
        # eventQ.put(["condition_load"])
    
    def load_condition_detail(self):
        # TODO 2024-12-06 조건식에 해당하는 종목 로드 요청
        self.ui.text_ouput.append("조건식 세부 종목 - 요청")
        # 000 : 항목명
        eventQ.put(["condition_detail", self.ui.list_condition.currentItem().text()])
    
    def account_changed(self, index):
        # account 클래스 변수에 계좌번호 업데이트
        self.account = self.ui.combo_account.currentText()
        print(f"계좌 변경 : {self.ui.combo_account.currentText()}")

        # TODO 2024-11-18 계좌 잔고, 예수금, 보유종목 요청
        eventQ.put(["account_info", self.account])

        # windowQ.put(f"계좌 [{self.account}] 상세정보 - 요청")
        self.ui.text_ouput.append(f"계좌 [{self.account}] 상세정보 - 요청")
        print(f"계좌 [{self.account}] 상세정보 - 요청")
        
    def login_kiwoom(self):
        # TODO 2024-11-13 로그인 유무 구분
        if self.ui.btn_login.text() != "로그인 완료":
            # eventQ.put(["login", ""])
            self.ui.text_ouput.append("로그인 - 요청")
        else:
            self.ui.text_ouput.append("이미 로그인 상태입니다.")
        
    def load_ohlcv(self):
        # eventQ.put(["ohlcv", ""])
        # windowQ.put("OHLCV - 로드")
        self.ui.text_output_2.append("OHLCV - 로드")
    
    def reset_output(self):
        self.ui.text_ouput.clear()
    
    def path_open(self):
        # 2021-04-01 지정된 경로를 open한다.
        # TODO 2024-12-03 OS별로 구분한다.
        
        path = self.ui.text_path.text()
        
        if self.os == "Windows":
            os.startfile(path)
        elif self.os  == "Darwin":  # macOS
            os.system(f"open {path}")
        else:  # Linux
            os.system(f"xdg-open {path}")
        # startfile(self.ui.text_path.text())
        # pass
        # startfile("c:/_db")
    
    def set_default_path(self):
        # 2021-04-01 기본 경로 설정
        default_path = "c:/data"
        self.ui.text_path.setText(default_path)
        self.settings.setValue("path", default_path)
        self.set_settings()
    
    def stock_list_item_clicked(self):
        #print(f"테이블 클릭 이벤트 발생")
        # TODO 2025-02-12 종목명, 종목코드 출력
        
        selected_table = self.sender()         
        
        selected_stock_name = selected_table.item(selected_table.currentRow(), 0).text()
        selected_stock_code = self.stock_to_code[selected_stock_name]
        
        self.current_stock_name = selected_stock_name
        
        # self.ui.text_output_2.append(f"선택된 종목 : {selected_stock_name} / {selected_stock_code}")
        # TODO 2025-02-12 해당종목 가격정보 요청(기간 없을 경우 120일)
        eventQ.put(["stock_price_load", selected_stock_name, selected_stock_code, self.settings.value("stock_price_range", "120")])
    
    # TODO 2025-02-25 일자별 주가 클릭 이벤트(바차트 로드)
    def stock_ohlcv_item_clicked(self):
        selected_table = self.sender()
        open_value = selected_table.item(selected_table.currentRow(), 1).text() # TODO 2025-02-27 시가는 계산할 필요없이 전달한다.
        selected_date = selected_table.item(selected_table.currentRow(), 0).text()
        
        selected_stock_code = self.stock_to_code[self.current_stock_name]
        
        # print(f"선택된 날짜 : {selected_date}")
        eventQ.put(["load_tick", self.current_stock_name, selected_stock_code, selected_date.replace('-', ''), open_value])

if __name__ == "__main__":
    eventQ, windowQ, settingsQ, dataQ, teleQ = Queue(), Queue(), Queue(), Queue(), Queue()
    qlist = [eventQ, windowQ, settingsQ, dataQ, teleQ]
    
    app = QApplication(sys.argv)

    my_app = MyApp()
    my_app.show()
    my_app.setWindowTitle("틱 다운로더")
    app.exec()