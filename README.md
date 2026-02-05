# Interview Transcription Summary System

3시간 인터뷰 transcript를 자동으로 처리하여 상세한 요약 문서(20-25페이지)를 생성하는 시스템입니다.

## ⚠️ 두 가지 사용 방법

### 방법 1: 웹 Claude 사용 (추천 - 추가 비용 없음) ✅

**Claude 맥스 플랜을 사용 중이라면 이 방법을 사용하세요!**

- ✅ **추가 비용 없음** (맥스 플랜에 포함)
- ✅ Projects + Artifacts 활용
- ❌ 수동 작업 필요 (30-40분 소요)

**가이드**: [WEB_CLAUDE_WORKFLOW.md](./WEB_CLAUDE_WORKFLOW.md)
**프롬프트 템플릿**: [PROMPTS_TEMPLATE.md](./PROMPTS_TEMPLATE.md)

### 방법 2: API 자동화 시스템 (추가 비용 발생) 💰

**정기적으로 많은 인터뷰를 처리하는 경우 이 방법을 사용하세요.**

- ✅ 완전 자동화 (5분 설정 + 자동 실행)
- ✅ 여러 인터뷰 배치 처리 가능
- ❌ **추가 비용**: 인터뷰당 약 $1.65 (Anthropic API 종량제)

**가이드**: 아래 설치 및 사용 방법 참조

---

## Context Window 한계 해결

- 긴 transcript를 한 번에 처리하지 않고 섹션별로 chunking
- 각 섹션을 독립적으로 처리하여 context window 한계 회피
- 섹션별 결과를 최종적으로 통합

## 비용 비교

### 간헐적 사용 (월 1-3회)
→ **웹 Claude 사용** 추천
- 시간: 30-40분/인터뷰
- 비용: $0 (맥스 플랜 $200/월에 포함)

### 정기적 사용 (주 3회 이상, 월 12회+)
→ **API 자동화** 고려
- 시간: 5분 설정 + 자동 실행
- 비용: 약 $20/월 (12회 × $1.65)
- 총 비용: 맥스 플랜 $200 + API $20 = $220/월

---

# API 자동화 시스템 사용 가이드

**주의**: 아래 내용은 API 자동화 시스템 사용시에만 필요합니다.
웹 Claude 사용 방법은 [WEB_CLAUDE_WORKFLOW.md](./WEB_CLAUDE_WORKFLOW.md)를 참조하세요.

## 설치 방법

```bash
pip install -r requirements.txt
```

## 환경 설정

`.env.example`을 `.env`로 복사하고 필요한 API 키를 설정하세요:

```bash
cp .env.example .env
```

필요한 API 키:
- `FIREFLIES_API_KEY`: Fireflies API 키
- `ANTHROPIC_API_KEY`: Claude API 키
- `GOOGLE_CREDENTIALS_PATH`: Google Cloud 서비스 계정 JSON 파일 경로

## 사용 방법

```bash
python src/main.py --transcript-id <fireflies_transcript_id>
```

또는 인터랙티브 모드:

```bash
python src/main.py
```

## 프로젝트 구조

```
sales-first-jobs/
├── src/
│   ├── fireflies_client.py      # Fireflies API 클라이언트
│   ├── transcript_processor.py  # Transcript 섹션 분할 로직
│   ├── claude_processor.py      # Claude API 통합 및 섹션 처리
│   ├── google_docs_client.py    # Google Docs API 클라이언트
│   └── main.py                  # 메인 워크플로우
├── config/
│   └── prompts.py               # Claude 프롬프트 템플릿
└── requirements.txt
```

## 워크플로우

1. Fireflies에서 transcript 가져오기
2. Transcript를 토픽/시간대별 섹션으로 자동 분할
3. 각 섹션을 Claude API로 개별 처리 (3-4페이지씩)
4. 처리된 섹션들을 하나의 문서로 통합
5. Google Docs에 최종 문서 업로드

## 출력 형식

각 섹션 문서에 포함되는 내용:
- 발언 내용의 직접 인용
- 맥락 설명
- 핵심 인사이트 하이라이트
- 검증 포인트 (확인이 필요한 사항들)
- 타임스탬프 및 화자 정보
