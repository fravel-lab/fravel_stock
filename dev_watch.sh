#!/bin/bash

# Fravel Stock Trader - 개발용 자동 감시 및 재시작 스크립트
# 사용법: chmod +x dev_watch.sh && ./dev_watch.sh

echo "🔍 Fravel Stock Trader - 개발 모드 시작"
echo "📁 감시 디렉토리: $(pwd)"
echo "⏳ Python 파일 변경 감지 중..."
echo "💡 Ctrl+C로 종료"
echo ""

watchmedo auto-restart \
  --directory=. \
  --pattern='*.py' \
  --ignore-patterns='__pycache__|*.pyc|*.db|*.pickle' \
  --recursive \
  --timeout=2 \
  -- python fravel_trader.py

echo "✅ 프로그램 종료"
