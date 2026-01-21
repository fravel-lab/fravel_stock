__author__ = 'spitz-pc'

from os import system

if __name__ == '__main__':
    # 2020-08-11 ui파일 삭제 후 생성되게 변경해야함
    # 2020-08-10 ui파일은 py파일로 변경한다.
    # 2020-10-23 틱다운로더 컨버팅 추가
    system("pyuic5 -x ./ui/fravel_trader.ui -o ./ui/fravel_trader_ui.py")
    print("트레이더 UI 컨버팅 완료")
