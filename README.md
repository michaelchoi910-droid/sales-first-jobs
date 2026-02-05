# Interview Transcription Summary System

3시간 인터뷰 transcript를 자동으로 처리하여 상세한 요약 문서(20-25페이지)를 생성하는 시스템입니다.

## 주요 기능

1. **Fireflies API 통합**: 녹음된 인터뷰 transcript 자동 가져오기
2. **자동 섹션 분할**: Timestamp와 토픽 기반으로 인터뷰를 의미있는 섹션으로 분할
3. **Claude API 처리**: 각 섹션을 개별적으로 상세하게 분석 및 요약
4. **Google Docs 통합**: 최종 문서를 자동으로 Google Docs에 업로드

## Context Window 한계 해결

- 긴 transcript를 한 번에 처리하지 않고 섹션별로 chunking
- 각 섹션을 독립적으로 처리하여 context window 한계 회피
- 섹션별 결과를 최종적으로 통합

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
