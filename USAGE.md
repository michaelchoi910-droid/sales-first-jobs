# 사용 가이드

## 빠른 시작

### 1. 설치

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 API 키 입력
```

### 2. API 키 설정

#### Fireflies API 키
1. https://app.fireflies.ai 로그인
2. Settings > Integrations > Custom Integrations
3. "Generate API Key" 클릭
4. 생성된 키를 `.env` 파일의 `FIREFLIES_API_KEY`에 입력

#### Anthropic Claude API 키
1. https://console.anthropic.com/ 로그인
2. "Get API Keys" 메뉴
3. "Create Key" 클릭
4. 생성된 키를 `.env` 파일의 `ANTHROPIC_API_KEY`에 입력

#### Google Cloud 설정 (선택사항)
Google Docs 업로드를 원하는 경우:

```bash
# Google 설정 가이드 보기
python src/main.py --setup-google
```

상세한 가이드를 따라 서비스 계정을 만들고 JSON 키 파일을 다운로드하세요.

### 3. 실행

```bash
# 인터랙티브 모드 (추천)
python src/main.py

# 특정 transcript ID로 실행
python src/main.py --transcript-id <YOUR_TRANSCRIPT_ID>

# 최근 transcript 목록 보기
python src/main.py --list-transcripts

# Transcript 검색
python src/main.py --search "세일즈 인터뷰"
```

## 사용 시나리오

### 시나리오 1: 첫 사용 (인터랙티브)

```bash
$ python src/main.py

🎙️  Interview Transcription Summary System
==========================================

No transcript ID provided. Enter a transcript ID or search term:
  - Enter transcript ID directly
  - Or type 'list' to see recent transcripts
  - Or type 'search <term>' to search

Enter your choice: list

Recent transcripts:

 1. [abc123] 세일즈 후보자 김철수 - 최종 인터뷰
 2. [def456] 세일즈 매니저 이영희 - 2차 면접
 ...

Select a transcript number (or enter ID): 1

# 이후 자동으로 처리가 진행됩니다
```

### 시나리오 2: 직접 ID 입력

```bash
# Fireflies에서 transcript ID를 이미 알고 있는 경우
python src/main.py --transcript-id "abc123def456"
```

### 시나리오 3: 검색 후 선택

```bash
# 키워드로 검색
python src/main.py --search "김철수"

# 또는 날짜로 검색
python src/main.py --search "2024-01"
```

### 시나리오 4: 로컬 저장만 (Google Docs 없이)

```bash
# Google Docs 업로드 건너뛰기
python src/main.py --transcript-id "abc123" --no-google-docs
```

## 고급 옵션

### 섹션 분할 방법 선택

```bash
# 시간 기반 분할 (30분 단위)
python src/main.py --transcript-id "abc123" --split-method time

# 토큰 기반 분할 (context window 한계 기준)
python src/main.py --transcript-id "abc123" --split-method tokens

# 토픽 기반 분할 (추천 - Claude가 주제 변화 감지)
python src/main.py --transcript-id "abc123" --split-method topics
```

### 섹션당 최대 토큰 조정

```bash
# 더 작은 섹션으로 분할 (더 안전하지만 섹션 수 증가)
python src/main.py --transcript-id "abc123" --max-tokens 3000

# 더 큰 섹션 허용 (섹션 수 감소하지만 context window 주의)
python src/main.py --transcript-id "abc123" --max-tokens 6000
```

### 출력 디렉토리 지정

```bash
# 특정 디렉토리에 저장
python src/main.py --transcript-id "abc123" --output-dir "/path/to/output"
```

## 출력 파일 구조

처리가 완료되면 다음과 같은 구조로 파일이 생성됩니다:

```
output/
└── 20240115_143022_abc123def/
    ├── complete_analysis.md       # 전체 분석 문서 (20-25페이지)
    ├── google_docs_url.txt        # Google Docs URL (업로드한 경우)
    └── sections/                  # 섹션별 개별 파일
        ├── section_01.md
        ├── section_02.md
        ├── section_03.md
        └── ...
```

### complete_analysis.md 구조

```markdown
# [인터뷰 제목]

## Executive Summary
- 후보자 핵심 프로필
- 주요 강점 Top 3
- 주요 우려사항 Top 3
- 최종 추천 의견

## 인터뷰 전체 흐름
...

## 핵심 역량 평가
### 세일즈 경험 및 성과
### 전문성 및 업계 지식
### 커뮤니케이션 및 대인관계
...

## 최종 평가 및 추천
...

## 섹션별 상세 분석
[각 섹션의 상세 분석...]
```

## 문제 해결

### Context Window 한계 문제

**증상**: Claude가 처리 중 멈추거나 에러 발생

**해결책**:
```bash
# 더 작은 섹션으로 분할
python src/main.py --transcript-id "abc123" --max-tokens 3000

# 또는 시간 기반 분할 사용 (15분 단위로 강제 분할)
python src/main.py --transcript-id "abc123" --split-method time
```

### API Rate Limit 문제

**증상**: "Rate limit exceeded" 에러

**해결책**: 스크립트에는 이미 자동 재시도와 백오프가 구현되어 있습니다.
대기 후 자동으로 재시도되므로 그대로 기다리면 됩니다.

### Google Docs 업로드 실패

**증상**: Google Docs 업로드 시 권한 에러

**해결책**:
```bash
# Google 설정 가이드 다시 확인
python src/main.py --setup-google

# 또는 로컬 저장만 사용
python src/main.py --transcript-id "abc123" --no-google-docs
```

### Fireflies Transcript를 찾을 수 없음

**증상**: "Transcript not found" 에러

**해결책**:
```bash
# 최근 transcript 목록 확인
python src/main.py --list-transcripts

# 또는 검색
python src/main.py --search "키워드"
```

## 비용 관리

### 예상 비용 (3시간 인터뷰 기준)

Claude API 비용 (Claude 3.5 Sonnet 기준):
- Input: 약 50,000 tokens (~$0.15)
- Output: 약 100,000 tokens (~$1.50)
- **총 예상 비용: 약 $1.65 per interview**

Fireflies API: 무료 (기본 플랜)
Google Docs API: 무료

### 비용 절감 팁

1. **더 작은 모델 사용** (정확도가 약간 떨어질 수 있음):
   ```python
   # src/claude_processor.py 수정
   model = "claude-3-5-haiku-20241022"  # Sonnet 대신 Haiku
   ```

2. **섹션 크기 증가** (context window 한계 주의):
   ```bash
   python src/main.py --max-tokens 6000
   ```

3. **일부 섹션만 처리**: 코드를 수정하여 특정 섹션만 선택적으로 처리

## 팁과 모범 사례

### 1. 인터뷰 전 준비
- Fireflies 녹음 품질 확인
- 화자 이름이 정확히 인식되는지 확인
- 3시간 인터뷰를 여러 세션으로 나누는 것도 고려

### 2. 결과 검토
- 생성된 문서를 반드시 검토
- 중요한 인용구가 정확한지 확인
- 검증 포인트를 실제로 체크

### 3. 워크플로우 최적화
- 정기적으로 실행하는 경우 cron job 설정 고려
- 결과를 팀과 공유하는 폴더 구조 만들기
- Google Drive 폴더 권한 관리

### 4. 데이터 보안
- `.env` 파일을 절대 공유하지 말 것
- Google 서비스 계정 JSON 키를 안전하게 보관
- 민감한 인터뷰 데이터는 암호화된 저장소 사용

## 추가 리소스

- [Fireflies API 문서](https://docs.fireflies.ai/)
- [Anthropic API 문서](https://docs.anthropic.com/)
- [Google Docs API 문서](https://developers.google.com/docs/api)

## 지원

이슈가 있거나 개선 제안이 있으면:
- GitHub Issues에 등록
- 또는 프로젝트 관리자에게 연락
