#!/usr/bin/env python3
"""
Fravel Stock Trader - 개발용 자동 감시 및 재시작 스크립트
watchdog를 사용하여 Python 파일 변경을 감지하고 자동으로 애플리케이션 재시작

사용법:
    python dev_watch_advanced.py
    또는
    chmod +x dev_watch_advanced.py && ./dev_watch_advanced.py
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import platform

# 개발 설정 임포트
try:
    from dev_config import IGNORE_PATTERNS, WATCH_PATTERNS, RESTART_TIMEOUT, get_log_message
except ImportError:
    print("❌ dev_config.py를 찾을 수 없습니다. 먼저 dev_config.py를 생성하세요.")
    sys.exit(1)


class FravelReloadHandler(FileSystemEventHandler):
    """파일 변경 감지 및 재시작 핸들러"""
    
    def __init__(self, app_name="fravel_trader.py"):
        self.app_name = app_name
        self.process = None
        self.should_restart = False
        self.last_restart_time = 0
        self.restart_delay = RESTART_TIMEOUT
        
        # 초기 프로세스 시작
        self.start_app()
    
    def should_ignore_path(self, path):
        """경로가 무시 목록에 있는지 확인"""
        path_str = str(path).lower()
        for pattern in IGNORE_PATTERNS:
            if pattern in path_str:
                return True
        return False
    
    def should_watch_path(self, path):
        """경로가 감시 대상인지 확인"""
        for pattern in WATCH_PATTERNS:
            if path.endswith(pattern.replace('*', '')):
                return True
        return False
    
    def start_app(self):
        """애플리케이션 시작"""
        if self.process and self.process.poll() is None:
            # 이미 실행 중이면 반환
            return
        
        print(get_log_message('start', f"{self.app_name} 시작 중..."))
        try:
            self.process = subprocess.Popen([sys.executable, self.app_name])
            print(get_log_message('success', f"{self.app_name} 시작됨 (PID: {self.process.pid})"))
        except Exception as e:
            print(get_log_message('error', f"애플리케이션 시작 실패: {e}"))
    
    def restart_app(self):
        """애플리케이션 재시작"""
        current_time = time.time()
        
        # 재시작 딜레이 체크 (너무 빈번한 재시작 방지)
        if current_time - self.last_restart_time < self.restart_delay:
            return
        
        self.last_restart_time = current_time
        
        print(get_log_message('warning', f"파일 변경 감지됨. {self.restart_delay}초 후 재시작합니다..."))
        
        # 기존 프로세스 종료
        if self.process and self.process.poll() is None:
            print(get_log_message('stop', "현재 프로세스 종료 중..."))
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(get_log_message('warning', "강제 종료 중..."))
                self.process.kill()
            except Exception as e:
                print(get_log_message('error', f"프로세스 종료 실패: {e}"))
        
        time.sleep(1)  # 잠깐의 대기
        
        # 새 프로세스 시작
        self.start_app()
    
    def on_modified(self, event):
        """파일 수정 감지"""
        if event.is_directory:
            return
        
        if self.should_ignore_path(event.src_path):
            return
        
        if not self.should_watch_path(event.src_path):
            return
        
        print(get_log_message('debug', f"파일 변경: {Path(event.src_path).name}"))
        self.restart_app()
    
    def on_created(self, event):
        """파일 생성 감지"""
        if event.is_directory:
            return
        
        if self.should_ignore_path(event.src_path):
            return
        
        if not self.should_watch_path(event.src_path):
            return
        
        print(get_log_message('debug', f"파일 생성: {Path(event.src_path).name}"))
    
    def shutdown(self):
        """애플리케이션 종료"""
        print(get_log_message('stop', "감시 종료 중..."))
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
        print(get_log_message('success', "모든 프로세스 종료됨"))


def signal_handler(signum, frame):
    """시그널 핸들러"""
    print(get_log_message('warning', "종료 신호 수신..."))
    if observer.is_alive():
        observer.stop()
        observer.join(timeout=5)
    
    if hasattr(handler, 'shutdown'):
        handler.shutdown()
    
    sys.exit(0)


def main():
    """메인 함수"""
    print("\n" + "="*60)
    print(get_log_message('start', "Fravel Stock Trader - 개발 모드 시작"))
    print("="*60)
    print(f"📁 감시 디렉토리: {os.getcwd()}")
    print(f"🔍 감시 대상: {WATCH_PATTERNS}")
    print(f"❌ 제외 패턴: {IGNORE_PATTERNS}")
    print(f"⏱️  재시작 딜레이: {RESTART_TIMEOUT}초")
    print(f"🖥️  OS: {platform.system()} {platform.release()}")
    print("="*60)
    print("💡 Ctrl+C로 종료\n")
    
    global observer, handler
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 파일 감시 설정
    handler = FravelReloadHandler()
    observer = Observer()
    observer.schedule(handler, path='.', recursive=True)
    
    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        print(get_log_message('error', f"예기치 않은 오류: {e}"))
        signal_handler(signal.SIGINT, None)


if __name__ == "__main__":
    main()
