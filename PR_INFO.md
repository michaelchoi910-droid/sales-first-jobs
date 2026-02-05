# Pull Request 정보

브랜치 `claude/interview-transcription-summary-hkc8t`가 성공적으로 푸시되었습니다!

## PR 생성 방법

### 옵션 1: GitHub 웹사이트에서 생성

1. 저장소로 이동: https://github.com/michaelchoi910-droid/sales-first-jobs
2. 상단에 노란색 배너가 보일 것입니다: "claude/interview-transcription-summary-hkc8t had recent pushes"
3. **"Compare & pull request"** 버튼 클릭
4. 아래 정보를 복사해서 사용하세요

### 옵션 2: 직접 URL로 이동

https://github.com/michaelchoi910-droid/sales-first-jobs/compare/main...claude/interview-transcription-summary-hkc8t

---

## PR 제목 (복사용)

```
인터뷰 Transcript 자동 분석 시스템 (Context Window 한계 해결)
```

---

## PR 설명 (복사용)

```markdown
## 개요

3시간 인터뷰 transcript를 자동으로 처리하여 상세한 요약 문서(20-25페이지)를 생성하는 시스템입니다.

Claude의 **context window 한계로 인해 처리가 중단되는 문제**를 해결했습니다.

## 주요 기능

### 🎯 Context Window 문제 해결
- 긴 transcript를 섹션별로 자동 chunking
- 각 섹션을 독립적으로 처리
- 최종 결과를 하나의 문서로 통합

### 🔧 핵심 모듈
1. **Fireflies API 통합**: 녹음된 인터뷰 자동 가져오기
2. **지능형 섹션 분할**: 시간/토큰/토픽 기반 분할
3. **Claude API 처리**: 각 섹션 상세 분석 (자동 재시도 포함)
4. **Google Docs 통합**: 최종 문서 자동 업로드

## 두 가지 사용 방법

### ✅ 방법 1: 웹 Claude (추가 비용 없음) - 추천
- Claude 맥스 플랜에 포함
- Projects + Artifacts 활용
- 수동 작업 (30-40분)
- **간헐적 사용자용** (월 1-3회)

📄 가이드: `WEB_CLAUDE_WORKFLOW.md`
📋 프롬프트: `PROMPTS_TEMPLATE.md`

### 💰 방법 2: API 자동화 (추가 비용 발생)
- 완전 자동화 (5분 설정 + 자동 실행)
- **정기적 사용자용** (주 3회 이상)
- 비용: 인터뷰당 $1.65

## 프로젝트 구조

```
sales-first-jobs/
├── src/
│   ├── fireflies_client.py      # Fireflies API 클라이언트
│   ├── transcript_processor.py  # 섹션 분할 (핵심!)
│   ├── claude_processor.py      # Claude API 처리
│   ├── google_docs_client.py    # Google Docs 업로드
│   ├── main.py                  # 메인 워크플로우
│   └── verify_setup.py          # 설정 검증
├── config/
│   └── prompts.py               # 최적화된 프롬프트
├── examples/
│   ├── quick_start.py           # 빠른 시작
│   └── batch_process.py         # 배치 처리
├── WEB_CLAUDE_WORKFLOW.md       # 웹 사용 가이드 (무료)
├── PROMPTS_TEMPLATE.md          # 프롬프트 템플릿
├── README.md                    # 프로젝트 소개
├── USAGE.md                     # 상세 가이드
└── requirements.txt             # Python 의존성
```

## API 자동화 빠른 시작

```bash
# 1. 설치
pip install -r requirements.txt

# 2. 환경 설정
cp .env.example .env
# .env 파일 편집 (API 키 입력)

# 3. 실행
python src/main.py --transcript-id <ID>

# 또는 인터랙티브 모드
python src/main.py
```

## 비용 비교

### 간헐적 사용 (월 1-3회)
→ **웹 Claude**: $0 (맥스 플랜 포함)

### 정기적 사용 (월 12회)
→ **API 자동화**: 약 $20/월 추가

## 주요 개선사항

### Before
❌ "Claude야 이 3시간 인터뷰 정리해줘"
→ Context window 한계로 중간에 멈춤

### After
✅ 자동으로 섹션 분할 → 각 섹션 독립 처리 → 통합
→ 20-25페이지 완벽한 분석 문서 생성

## 문서

- `README.md`: 프로젝트 개요
- `WEB_CLAUDE_WORKFLOW.md`: 웹 사용 가이드 (무료)
- `PROMPTS_TEMPLATE.md`: 복사-붙여넣기 프롬프트
- `USAGE.md`: API 자동화 상세 가이드

## 다음 단계

1. **지금**: 웹 Claude 워크플로우 사용 (추가 비용 없음)
2. **나중**: 인터뷰 빈도가 증가하면 API 자동화로 전환

## 테스트 상태

- ✅ 모든 모듈 구현 완료
- ✅ 에러 처리 및 재시도 로직 포함
- ✅ 문서화 완료
- ⚠️  실제 API 키로 테스트 필요

## 추가된 파일

### 핵심 시스템
- `src/fireflies_client.py` - Fireflies API 통합
- `src/transcript_processor.py` - 섹션 분할 로직
- `src/claude_processor.py` - Claude API 처리
- `src/google_docs_client.py` - Google Docs 업로드
- `src/main.py` - 메인 워크플로우

### 문서
- `WEB_CLAUDE_WORKFLOW.md` - 웹 Claude 사용 가이드
- `PROMPTS_TEMPLATE.md` - 프롬프트 템플릿
- `README.md` - 프로젝트 소개
- `USAGE.md` - 상세 사용 가이드

### 설정
- `requirements.txt` - Python 의존성
- `.env.example` - 환경 변수 템플릿
- `.gitignore` - Git 제외 파일
```

---

## 체크리스트

PR 생성 전 확인:
- [x] 모든 파일 커밋됨
- [x] 브랜치 푸시됨
- [x] 문서화 완료
- [ ] PR 생성 (GitHub 웹사이트에서)
- [ ] 나중에 필요할 때 merge

---

## 빠른 링크

- 저장소: https://github.com/michaelchoi910-droid/sales-first-jobs
- PR 생성: https://github.com/michaelchoi910-droid/sales-first-jobs/compare/main...claude/interview-transcription-summary-hkc8t
- 브랜치: `claude/interview-transcription-summary-hkc8t`
