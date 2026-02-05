#!/usr/bin/env python3
"""
Demo script: Process mock interview transcript with Claude API
완전 자동화 시연
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
import sys

# Add src to path
sys.path.insert(0, '/home/user/sales-first-jobs')

# Load environment variables
load_dotenv()


def load_mock_transcript():
    """Load mock interview transcript"""
    with open('test_data/sample_interview.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def create_transcript_sections(transcript_data):
    """Convert mock data to TranscriptSection-like objects"""
    from src.fireflies_client import TranscriptSentence, TranscriptData

    # Convert sentences
    sentences = [
        TranscriptSentence(
            text=s['text'],
            speaker_name=s['speaker_name'],
            start_time=s['start_time'],
            end_time=s['end_time']
        )
        for s in transcript_data['sentences']
    ]

    # Create TranscriptData
    return TranscriptData(
        transcript_id=transcript_data['transcript_id'],
        title=transcript_data['title'],
        date=datetime.fromisoformat(transcript_data['date'].replace('Z', '+00:00')),
        duration=transcript_data['duration'],
        sentences=sentences,
        participants=transcript_data['participants']
    )


def main():
    print("=" * 80)
    print("  🎙️  Interview Transcription Summary System - DEMO")
    print("=" * 80)
    print()
    print("완전 자동화 시연을 시작합니다...")
    print()

    # Step 1: Load mock transcript
    print("[Step 1/5] 📥 Mock 인터뷰 Transcript 로드...")
    try:
        mock_data = load_mock_transcript()
        transcript = create_transcript_sections(mock_data)
        print(f"✅ Transcript 로드 완료!")
        print(f"   제목: {transcript.title}")
        print(f"   날짜: {transcript.date.strftime('%Y-%m-%d %H:%M')}")
        print(f"   시간: {transcript.duration_formatted}")
        print(f"   문장 수: {len(transcript.sentences):,}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # Step 2: Split into sections
    print("[Step 2/5] ✂️  Transcript 섹션 분할...")
    try:
        from src.transcript_processor import TranscriptProcessor

        processor = TranscriptProcessor(max_tokens_per_section=2000)  # 작게 설정

        # 토큰 기반 분할 (더 안전)
        sections = processor.split_by_tokens(transcript, max_tokens=2000)

        print(f"✅ 섹션 분할 완료!")
        print(f"   총 섹션 수: {len(sections)}")
        print()

        for section in sections:
            print(f"   섹션 {section.section_number}:")
            print(f"     - 시간: {section.start_time_formatted} - {section.end_time_formatted}")
            print(f"     - 토큰: {section.token_count:,}")
            print(f"     - 문장: {len(section.sentences)}")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 3: Process with Claude API
    print("[Step 3/5] 🤖 Claude API로 섹션 처리 중...")
    print()

    try:
        from src.claude_processor import ClaudeProcessor

        claude = ClaudeProcessor(
            model="claude-3-5-haiku-20241022",  # Haiku로 테스트 (더 저렴)
            max_tokens=4000
        )

        # 첫 섹션만 처리 (시연용)
        print(f"⚠️  시연을 위해 첫 섹션만 처리합니다.")
        print(f"   (실제 사용시에는 모든 섹션을 자동 처리)")
        print()

        processed_section = claude.process_section(
            sections[0],
            interview_title=transcript.title,
            interview_date=transcript.date.strftime('%Y-%m-%d')
        )

        print()
        print("=" * 80)
        print("✅ 섹션 처리 완료!")
        print("=" * 80)
        print()
        print("📊 처리 결과:")
        print(f"   - 섹션: {processed_section.section_title}")
        print(f"   - 입력 토큰: {processed_section.token_usage['input_tokens']:,}")
        print(f"   - 출력 토큰: {processed_section.token_usage['output_tokens']:,}")
        print()

        print("=" * 80)
        print("📄 생성된 분석 내용 (미리보기):")
        print("=" * 80)
        print()

        # 분석 내용의 처음 1000자만 표시
        preview = processed_section.analysis[:1000]
        print(preview)
        print()
        print(f"... (총 {len(processed_section.analysis):,}자)")
        print()

    except Exception as e:
        print(f"❌ Claude API Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("💡 Tip: Anthropic API 키가 올바른지, 크레딧이 있는지 확인해주세요.")
        print(f"   https://console.anthropic.com/")
        return

    # Step 4: Save locally
    print("[Step 4/5] 💾 로컬에 저장...")
    try:
        os.makedirs('output', exist_ok=True)

        output_file = 'output/demo_section_analysis.md'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {processed_section.section_title}\n\n")
            f.write(f"**인터뷰**: {transcript.title}\n")
            f.write(f"**시간**: {processed_section.start_time} - {processed_section.end_time}\n\n")
            f.write("---\n\n")
            f.write(processed_section.analysis)

        print(f"✅ 저장 완료: {output_file}")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # Step 5: Summary
    print("[Step 5/5] 📊 최종 요약")
    print("=" * 80)
    print()
    print("✅ 자동화 시연 완료!")
    print()
    print("📁 생성된 파일:")
    print(f"   - {output_file}")
    print()
    print("💰 비용 예상:")
    input_tokens = processed_section.token_usage['input_tokens']
    output_tokens = processed_section.token_usage['output_tokens']

    # Haiku pricing: $0.25 per MTok input, $1.25 per MTok output
    cost = (input_tokens / 1_000_000 * 0.25) + (output_tokens / 1_000_000 * 1.25)

    print(f"   - 입력 토큰: {input_tokens:,} tokens")
    print(f"   - 출력 토큰: {output_tokens:,} tokens")
    print(f"   - 이 섹션 비용: ${cost:.4f}")
    print(f"   - 전체 인터뷰({len(sections)}섹션) 예상: ${cost * len(sections):.2f}")
    print()
    print("=" * 80)
    print()
    print("🚀 실제 사용:")
    print("   python src/main.py --transcript-id <fireflies_id>")
    print()


if __name__ == '__main__':
    main()
