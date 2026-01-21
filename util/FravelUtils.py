from math import trunc
from os import mkdir
from os.path import isdir

import psutil
import pyqtgraph as pg
from PyQt5.QtGui import QPalette, QColor, QBrush
from PyQt5.QtWidgets import qApp

__author__ = 'spitz-pc'

WHITE = QColor(255, 255, 255)
BLACK = QColor(0, 0, 0)
RED = QColor(255, 0, 0)
PRIMARY = QColor(53, 53, 53)
SECONDARY = QColor(35, 35, 35)
TERTIARY = QColor(42, 130, 218)


def chk_dir(_dir):
    directory = _dir
    if isdir(directory) is False:
        mkdir(directory)
        print(directory + " - 디렉토리 생성완료")


def remove_comma(data):
    # 2020-07-29 가격의 콤마 제거
    return data.replace(",", "")


def css_rgb(color, a=False):
    """Get a CSS `rgb` or `rgba` string from a `QtGui.QColor`."""
    return ("rgba({}, {}, {}, {})" if a else "rgb({}, {}, {})").format(*color.getRgb())


def set_dark_theme():
    qApp.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, PRIMARY)
    dark_palette.setColor(QPalette.WindowText, WHITE)
    dark_palette.setColor(QPalette.Base, SECONDARY)
    dark_palette.setColor(QPalette.AlternateBase, PRIMARY)
    dark_palette.setColor(QPalette.ToolTipBase, WHITE)
    dark_palette.setColor(QPalette.ToolTipText, WHITE)
    dark_palette.setColor(QPalette.Text, WHITE)
    dark_palette.setColor(QPalette.Button, PRIMARY)
    dark_palette.setColor(QPalette.ButtonText, WHITE)
    dark_palette.setColor(QPalette.BrightText, RED)
    dark_palette.setColor(QPalette.Link, TERTIARY)
    dark_palette.setColor(QPalette.Highlight, TERTIARY)
    dark_palette.setColor(QPalette.HighlightedText, BLACK)
    qApp.setPalette(dark_palette)
    qApp.setStyleSheet("QToolTip {{"
                    "color: {white};"
                    "background-color: {tertiary};"
                    "border: 1px solid {white};"
                    "}}".format(white=css_rgb(WHITE), tertiary=css_rgb(TERTIARY)))


def clear_table(_table):
    # 2021-04-20 테이블을 초기화시킨다.
    while _table.rowCount() > 0:
        _table.removeRow(0)


def get_cpu_memory_info():
    cpu = psutil.cpu_times_percent()
    cpu = 100 - cpu.idle
    # print("cpu 사용율 {}".format(round(cpu, 2))) # 소수점 반올림

    mem = psutil.virtual_memory()
    # print("메모리 {}%".format(mem.percent))

    return "CPU : {}% | MEMORY : {}%".format(round(cpu, 2), mem.percent)


def num_to_time(_num_time):
    # ex: 101112
    return _num_time[0:2] + "시 " + _num_time[2:4] + "분 " + _num_time[4:6] + "초"


def insert_comma(data):
    # 2020-07-24 1,000단위 콤마 입력(음수는 유지)
    strip_data = data.lstrip('-0')
    if strip_data == '' or strip_data == '.00':
        strip_data = '0'
    try:
        format_data = format(int(strip_data), ',d')
    except:
        format_data = format(float(strip_data))

    if data.startswith('-'):
        format_data = '-' + format_data

    return format_data


def set_item_color(_item, _text):
    # 2020-06-19 주가 +,- 색 지정
    if _text.startswith("-"):
        # _item.setForeground(QBrush(QColor(18, 72, 194)))
        _item.setForeground(QBrush(QColor(3, 169, 244)))
    else:
        # _item.setForeground(QBrush(QColor(230, 30, 9)))
        _item.setForeground(QBrush(QColor(255, 65, 129)))


def create_dir(_dir):
    directory = _dir
    if isdir(directory) is False:
        mkdir(directory)
        print(directory + " - 디렉토리 생성완료")


class NonScientific(pg.AxisItem):
    # 2021-02-16 100만단위 이상의 값도 그대로 출력(지수표현 X)
    def __init__(self, *args, **kwargs):
        super(NonScientific, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        tmp_value = []
        for value in values:
            if value > 1000000:
                tmp = trunc(value / 1000)  # 소수점 제거
                tmp = format(tmp, ",")  # 천단위 콤마 추가
                tmp = "{}K".format(tmp)  # K표시
                tmp_value.append(tmp)
            else:
                tmp = trunc(value)  # 소수점 제거
                tmp = format(tmp, ",")  # 천단위 콤마 추가
                tmp_value.append(tmp)
            #     return [format(value, ',') for value in values]  # This line return the NonScientific notation value
            # return [format(value, ',')]  # This line return the NonScientific notation value
        return tmp_value
        # return [format(value, ',') for value in values]  # This line return the NonScientific notation value


def change_format(text, dotdowndel=False, dotdown8=False):
    text = str(text)
    try:
        format_data = format(int(text), ',')
    except ValueError:
        format_data = format(float(text), ',')
        if len(format_data.split('.')) >= 2:
            if dotdowndel:
                format_data = format_data.split('.')[0]
            elif dotdown8:
                if len(format_data.split('.')[1]) == 1:
                    format_data += '0000000'
                elif len(format_data.split('.')[1]) == 2:
                    format_data += '000000'
                elif len(format_data.split('.')[1]) == 3:
                    format_data += '00000'
                elif len(format_data.split('.')[1]) == 4:
                    format_data += '0000'
                elif len(format_data.split('.')[1]) == 5:
                    format_data += '000'
                elif len(format_data.split('.')[1]) == 6:
                    format_data += '00'
                elif len(format_data.split('.')[1]) == 7:
                    format_data += '0'
            elif len(format_data.split('.')[1]) == 1:
                format_data += '0'
    return format_data
