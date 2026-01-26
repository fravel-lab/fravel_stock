"""
개발 모드 설정 파일
상황에 따라 아래 설정을 변경하여 사용
"""

import os
from datetime import datetime

# 개발 모드 활성화
DEV_MODE = True

# 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = "DEBUG"

# 자동 재시작 감시 활성화
AUTO_RESTART_ENABLED = True

# 감시 제외 패턴
IGNORE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '*.db',
    '*.pickle',
    '.git',
    '.idea',
    'venv',
    '__pycache__'
]

# 감시 패턴
WATCH_PATTERNS = ['*.py']

# 재시작 타임아웃 (초)
RESTART_TIMEOUT = 2

def get_log_message(msg_type, message):
    """로그 메시지 포맷"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    symbols = {
        'info': '📋',
        'debug': '🔍',
        'warning': '⚠️',
        'error': '❌',
        'success': '✅',
        'start': '🚀',
        'stop': '🛑'
    }
    symbol = symbols.get(msg_type, '•')
    return f"[{timestamp}] {symbol} {message}"

if __name__ == "__main__":
    print(get_log_message('info', "개발 모드 설정 로드됨"))
    print(f"  - DEV_MODE: {DEV_MODE}")
    print(f"  - LOG_LEVEL: {LOG_LEVEL}")
    print(f"  - AUTO_RESTART_ENABLED: {AUTO_RESTART_ENABLED}")
