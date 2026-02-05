# 🤖 완전 자동화 가이드

Fireflies에 녹음이 업로드되면 **자동으로** 처리하여 Google Docs에 문서를 생성합니다.

## 작동 방식

1. **모니터 프로그램**이 5분마다 Fireflies를 체크
2. 새 인터뷰 발견 → **자동 처리 시작**
3. Claude API로 분석 → Google Docs 생성
4. **손 하나 안 대고 완료!** ✨

---

## 초기 설정 (한 번만)

### 1. 저장소 Clone 및 설치

```bash
cd ~/Documents
git clone https://github.com/michaelchoi910-droid/sales-first-jobs.git
cd sales-first-jobs
git checkout claude/interview-transcription-summary-hkc8t
pip3 install -r requirements.txt
```

### 2. API 키 확인

`.env` 파일이 이미 있는지 확인:

```bash
cat .env
```

없으면 생성:

```bash
cp .env.example .env
# 편집기로 열어서 API 키 입력
nano .env
```

### 3. Google Cloud 설정 (선택사항)

Google Docs 자동 업로드를 원하면:

#### 3.1 서비스 계정 생성

```bash
python src/main.py --setup-google
```

가이드를 따라 서비스 계정 생성 후 JSON 키 파일 다운로드

#### 3.2 Google Drive 폴더 설정 (추천!)

특정 폴더에 문서를 자동으로 생성하려면:

**방법 1: 자동 설정 (쉬움)** ⭐
```bash
python3 find_google_folder.py
```

대화형으로 폴더를 선택하면 자동으로 config.py에 설정됩니다.

**방법 2: 수동 설정**

1. Google Drive에서 원하는 폴더 열기
2. URL에서 폴더 ID 복사:
   ```
   https://drive.google.com/drive/folders/[여기가_폴더_ID]
   ```
3. `config.py` 파일 편집:
   ```python
   GOOGLE_DRIVE_FOLDER_ID = "복사한_폴더_ID"
   ```

**방법 3: URL로 설정**
```bash
python3 find_google_folder.py
# 옵션 2 선택 → URL 붙여넣기
```

---

## 자동화 실행

### 방법 1: 터미널에서 실행 (간단)

```bash
cd ~/Documents/sales-first-jobs
python3 auto_monitor.py
```

**장점**: 바로 시작, 로그 바로 확인
**단점**: 터미널 닫으면 종료됨

### 방법 2: 백그라운드 실행 (추천)

```bash
cd ~/Documents/sales-first-jobs
nohup python3 auto_monitor.py > monitor.log 2>&1 &
```

**장점**: 터미널 닫아도 계속 실행
**단점**: 수동으로 종료해야 함

로그 확인:
```bash
tail -f ~/Documents/sales-first-jobs/monitor.log
```

프로세스 종료:
```bash
ps aux | grep auto_monitor
kill <PID>
```

### 방법 3: macOS 서비스로 등록 (가장 안정적) ⭐

맥북 재부팅해도 자동 재시작!

#### 3.1 서비스 파일 생성

```bash
nano ~/Library/LaunchAgents/com.salesfirst.interview-monitor.plist
```

아래 내용 붙여넣기:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.salesfirst.interview-monitor</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/YOUR_USERNAME/Documents/sales-first-jobs/auto_monitor.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/Documents/sales-first-jobs</string>

    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/Documents/sales-first-jobs/monitor.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/Documents/sales-first-jobs/monitor_error.log</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

**⚠️ 중요**: `YOUR_USERNAME`을 실제 사용자명으로 변경!

사용자명 확인:
```bash
whoami
```

#### 3.2 서비스 시작

```bash
launchctl load ~/Library/LaunchAgents/com.salesfirst.interview-monitor.plist
```

#### 3.3 서비스 상태 확인

```bash
launchctl list | grep interview-monitor
```

#### 3.4 서비스 중지

```bash
launchctl unload ~/Library/LaunchAgents/com.salesfirst.interview-monitor.plist
```

---

## 사용 흐름

### 1단계: 자동화 시작

```bash
# 방법 2 (백그라운드)
cd ~/Documents/sales-first-jobs
nohup python3 auto_monitor.py > monitor.log 2>&1 &

# 또는 방법 3 (서비스)
launchctl load ~/Library/LaunchAgents/com.salesfirst.interview-monitor.plist
```

### 2단계: Fireflies에 녹음 업로드

평소처럼 Fireflies에 인터뷰 녹음 업로드

### 3단계: 자동 처리 확인

5분 이내에 자동으로:
1. ✅ 새 인터뷰 감지
2. ✅ Claude API 분석
3. ✅ Google Docs 생성

로그 확인:
```bash
tail -f ~/Documents/sales-first-jobs/monitor.log
```

### 4단계: 결과 확인

```
output/20240205_143022_abc123/
├── complete_analysis.md
└── google_docs_url.txt  # Google Docs 링크
```

---

## 모니터링 및 관리

### 로그 확인

```bash
# 실시간 로그
tail -f ~/Documents/sales-first-jobs/monitor.log

# 최근 50줄
tail -50 ~/Documents/sales-first-jobs/monitor.log

# 에러 로그
tail -f ~/Documents/sales-first-jobs/monitor_error.log
```

### 처리된 인터뷰 목록

```bash
cat ~/Documents/sales-first-jobs/.processed_transcripts.json
```

### 프로세스 상태 확인

```bash
ps aux | grep auto_monitor
```

### 수동 재시작

```bash
# 프로세스 찾기
ps aux | grep auto_monitor

# 종료
kill <PID>

# 재시작
cd ~/Documents/sales-first-jobs
nohup python3 auto_monitor.py > monitor.log 2>&1 &
```

---

## 문제 해결

### "새 인터뷰가 처리되지 않아요"

1. 로그 확인:
   ```bash
   tail -100 ~/Documents/sales-first-jobs/monitor.log
   ```

2. 프로세스 실행 중인지 확인:
   ```bash
   ps aux | grep auto_monitor
   ```

3. API 키 확인:
   ```bash
   cat ~/Documents/sales-first-jobs/.env
   ```

### "Google Docs 업로드가 안 돼요"

로컬 파일은 생성되지만 Google Docs 업로드 실패 시:

```bash
python src/main.py --setup-google
```

가이드를 따라 Google Cloud 설정

### "비용이 너무 많이 나와요"

Haiku 모델로 변경 (더 저렴):

`auto_monitor.py` 파일 수정:
```python
# Line ~120
claude = ClaudeProcessor(
    model="claude-3-5-haiku-20241022",  # 변경
    max_tokens=8000
)
```

---

## 비용 관리

### 예상 비용

- **1시간 인터뷰**: ~$0.50
- **3시간 인터뷰**: ~$1.50
- **월 12회 인터뷰**: ~$18

### 비용 최적화

1. **Haiku 모델 사용** (3-5배 저렴)
2. **체크 주기 늘리기** (10분 → 30분)
3. **특정 제목만 필터링**

---

## 고급 설정

### 체크 주기 변경

`auto_monitor.py` 파일 수정:

```python
# Line ~200
CHECK_INTERVAL = 600  # 10분 (기본: 300초 = 5분)
```

### 특정 제목만 처리

`auto_monitor.py`에 필터 추가:

```python
# Line ~80 근처
new_transcripts = [
    t for t in transcripts
    if t['id'] not in processed_ids
    and '사이드바이사이드' in t['title']  # 추가
]
```

### 알림 추가 (Slack, Email 등)

나중에 필요하면 알림 통합 가능

---

## 완전 자동화 체크리스트

- [ ] 저장소 clone 완료
- [ ] 의존성 설치 완료
- [ ] .env 파일 API 키 설정
- [ ] Google Cloud 설정 (선택)
- [ ] 자동화 스크립트 실행
- [ ] 로그 확인으로 정상 작동 확인
- [ ] 테스트 인터뷰 업로드
- [ ] 5-10분 후 자동 처리 확인
- [ ] Google Docs 문서 생성 확인

---

## 요약

### 초기 설정 (한 번만)

```bash
cd ~/Documents
git clone https://github.com/michaelchoi910-droid/sales-first-jobs.git
cd sales-first-jobs
git checkout claude/interview-transcription-summary-hkc8t
pip3 install -r requirements.txt
```

### 실행 (항상)

```bash
cd ~/Documents/sales-first-jobs
nohup python3 auto_monitor.py > monitor.log 2>&1 &
```

### 확인

```bash
tail -f ~/Documents/sales-first-jobs/monitor.log
```

---

**이제 완전 자동화입니다!** 🎉

Fireflies에 업로드만 하면 자동으로 Google Docs에 분석 문서가 생성됩니다!
