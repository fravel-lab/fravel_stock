# Fravel Stock Trader - 개발용 자동 감시 및 재시작 가이드

## 개요

이 프로젝트는 watchdog를 사용하여 Python 파일 변경을 자동으로 감지하고 애플리케이션을 재시작하는 개발 환경을 제공합니다.

## 설치

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

또는 watchdog만 설치:

```bash
pip install watchdog
```

## 사용 방법

### 방법 1: Bash 스크립트 (간단)

```bash
# 실행 권한 부여
chmod +x dev_watch.sh

# 실행
./dev_watch.sh
```

**장점:**
- ✅ 가장 간단함
- ✅ 추가 설정 불필요
- ✅ Linux/macOS 네이티브

**단점:**
- ❌ Windows에서는 WSL 필요
- ❌ 상세한 로그 없음

---

### 방법 2: Python 고급 버전 (추천) ⭐

```bash
python dev_watch_advanced.py
```

**장점:**
- ✅ 모든 OS 지원 (Windows/macOS/Linux)
- ✅ 상세한 로그 및 타임스탬프
- ✅ 안정적인 재시작 로직
- ✅ 설정 파일(`dev_config.py`)로 커스터마이징 가능
- ✅ 프로세스 상태 관리

**단점:**
- ❌ Python 스크립트 복잡도 증가

---

## 파일 설명

| 파일 | 설명 |
|------|------|
| `dev_watch.sh` | Bash 기반 간단한 감시 스크립트 |
| `dev_watch_advanced.py` | Python 기반 고급 감시 스크립트 (추천) |
| `dev_config.py` | 개발 모드 설정 파일 |
| `requirements.txt` | 의존성 패키지 목록 |

---

## 작동 원리

### Bash 버전 (`dev_watch.sh`)
```
파일 변경 감지 → 전체 애플리케이션 재시작
```

### Python 버전 (`dev_watch_advanced.py`)
```
파일 변경 감지 
  ↓ (2초 딜레이)
기존 프로세스 종료 (SIGTERM)
  ↓
새 프로세스 시작
  ↓
로그 출력 (타임스탬프 포함)
```

---

## 감시 설정

### `dev_config.py`에서 커스터마이징

```python
# 감시 제외 패턴 (변경하지 마세요)
IGNORE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '*.db',
    '*.pickle',
]

# 감시 대상 (Python 파일만)
WATCH_PATTERNS = ['*.py']

# 재시작 딜레이 (너무 빠른 재시작 방지)
RESTART_TIMEOUT = 2  # 초
```

---

## 주의사항

### ⚠️ 상태 손실
- 애플리케이션이 재시작되므로 **메모리의 모든 상태가 초기화**됩니다
- API 토큰, 계좌 정보, UI 입력값 등이 손실됩니다
- 이는 **정상적인 동작**입니다

### ⚠️ 재시작 타이밍
- 파일 저장 후 2초 딜레이 후 재시작
- 너무 빈번한 저장 시 마지막 변경만 반영됩니다

### ⚠️ 멀티프로세싱
- 메인 프로세스 재시작 시 `KiwoomWorker`, `TelegramWorker` 등 자식 프로세스도 재시작됩니다
- 이는 의도된 동작입니다

---

## 문제 해결

### Q: "watchdog 모듈을 찾을 수 없다" 에러
**A:** watchdog 설치 확인
```bash
pip install watchdog
pip show watchdog
```

### Q: "dev_config.py를 찾을 수 없다" 에러
**A:** 스크립트를 프로젝트 루트에서 실행하세요
```bash
cd /Users/spitz/GitHub/fravel_stock
python dev_watch_advanced.py
```

### Q: Windows에서 작동 안 함
**A:** Python 버전 사용
```bash
python dev_watch_advanced.py
```

### Q: 프로세스가 재시작 안 됨
**A:** 권한 확인
```bash
# Bash 버전 실행 권한 확인
ls -l dev_watch.sh
# rw- 이면 권한 없음, 다시 설정
chmod +x dev_watch.sh
```

---

## 고급 사용법

### 커스텀 재시작 스크립트

`dev_watch_advanced.py`의 `start_app()` 메서드 수정:

```python
def start_app(self):
    # 커스텀 환경 변수 설정
    env = os.environ.copy()
    env['DEV_MODE'] = 'True'
    
    self.process = subprocess.Popen([sys.executable, self.app_name], env=env)
```

### 특정 파일만 감시

`dev_config.py` 수정:

```python
WATCH_PATTERNS = ['*.py', 'ui/fravel_trader_ui.py']  # UI 파일만 감시
```

---

## 권장 개발 워크플로우

1. **터미널 1**: 개발 감시 스크립트 실행
   ```bash
   python dev_watch_advanced.py
   ```

2. **터미널 2**: 코드 편집
   ```bash
   # IDE에서 코드 수정 후 저장
   # → 자동으로 재시작됨
   ```

3. **문제 발생 시**: Ctrl+C로 스크립트 종료
   ```bash
   # 스크립트 중지
   Ctrl+C
   
   # 직접 실행
   python fravel_trader.py
   ```

---

## 비교: 개발 환경 옵션

| 옵션 | 재시작 시간 | 상태 유지 | 설정 복잡도 |
|------|----------|---------|-----------|
| 수동 재시작 | - | ❌ | 낮음 |
| watchdog (Bash) | 1-2초 | ❌ | 낮음 |
| watchdog (Python) | 1-2초 | ❌ | 중간 |
| Reloadium (PyCharm Pro) | 0.5초 | ✅ | 높음 |

---

## 라이선스

이 스크립트는 프로젝트와 동일한 라이선스를 따릅니다.

---

## 피드백

문제나 개선 사항이 있으면 이슈를 등록해주세요!
