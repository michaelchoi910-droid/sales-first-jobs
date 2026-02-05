#!/usr/bin/env python3
"""
🎯 원클릭 자동화: 사이드바이사이드 이요한님 커피챗 분석
완전 자동으로 20-25페이지 분석 문서를 생성합니다.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, '/home/user/sales-first-jobs')

# Load environment variables
load_dotenv()


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")


def main():
    # Target transcript
    TRANSCRIPT_ID = "-260202-160214::01KGEVQY174T8VF1AK9R55DE1W"

    print_header("🎙️  완전 자동화: 사이드바이사이드 이요한님 커피챗")
    print("손 안대고 전체 프로세스를 자동으로 실행합니다...")
    print()
    print(f"📋 Transcript ID: {TRANSCRIPT_ID}")
    print()
    print("⏱️  예상 소요 시간: 5-10분 (인터뷰 길이에 따라)")
    print("💰 예상 비용: $1.50-2.00")
    print()
    input("🚀 시작하려면 Enter를 누르세요...")
    print()

    try:
        # Import modules
        from src.fireflies_client import FirefliesClient
        from src.transcript_processor import TranscriptProcessor
        from src.claude_processor import ClaudeProcessor

        # Step 1: Fetch transcript
        print_header("Step 1/5: 📥 Fireflies에서 Transcript 가져오기")

        fireflies = FirefliesClient()
        transcript = fireflies.get_transcript(TRANSCRIPT_ID)

        print(f"✅ Transcript 가져오기 완료!")
        print(f"   제목: {transcript.title}")
        print(f"   날짜: {transcript.date.strftime('%Y-%m-%d %H:%M')}")
        print(f"   시간: {transcript.duration_formatted}")
        print(f"   문장 수: {len(transcript.sentences):,}")
        print(f"   참석자: {', '.join(transcript.participants)}")

        # Step 2: Split into sections
        print_header("Step 2/5: ✂️  Transcript 섹션 분할")

        processor = TranscriptProcessor(max_tokens_per_section=4000)

        # Use topic-based splitting for best quality
        print("🤖 Claude가 주제를 분석하여 섹션을 나눕니다...")
        sections = processor.split_with_topic_detection(
            transcript,
            min_section_minutes=15,
            max_tokens=4000
        )

        print(f"\n✅ 섹션 분할 완료!")
        print(f"   총 섹션: {len(sections)}")
        print()
        print(processor.get_section_summary(sections))

        # Step 3: Process with Claude
        print_header("Step 3/5: 🤖 Claude API로 각 섹션 분석")

        claude = ClaudeProcessor(
            model="claude-3-7-sonnet-20250219",  # Sonnet for best quality
            max_tokens=16000
        )

        processed_sections = claude.process_all_sections(
            sections,
            interview_title=transcript.title,
            interview_date=transcript.date.strftime('%Y-%m-%d')
        )

        # Step 4: Synthesize final document
        print_header("Step 4/5: 📝 최종 문서 통합")

        final_synthesis = claude.synthesize_final_document(
            processed_sections,
            interview_title=transcript.title,
            interview_date=transcript.date.strftime('%Y-%m-%d'),
            total_duration=transcript.duration_formatted,
            participants=transcript.participants
        )

        complete_document = claude.create_complete_document(
            processed_sections,
            final_synthesis,
            interview_title=transcript.title,
            interview_date=transcript.date.strftime('%Y-%m-%d')
        )

        # Step 5: Save locally
        print_header("Step 5/5: 💾 결과 저장")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join('output', f"{timestamp}_yohan_coffee_chat")
        os.makedirs(output_dir, exist_ok=True)

        # Save complete document
        complete_path = os.path.join(output_dir, "complete_analysis.md")
        claude.save_document(complete_document, complete_path)

        # Save sections separately
        sections_dir = os.path.join(output_dir, "sections")
        claude.save_sections_separately(
            processed_sections,
            sections_dir,
            transcript.title
        )

        # Calculate costs
        total_input = sum(ps.token_usage['input_tokens'] for ps in processed_sections)
        total_output = sum(ps.token_usage['output_tokens'] for ps in processed_sections)

        # Sonnet pricing: $3 per MTok input, $15 per MTok output
        cost = (total_input / 1_000_000 * 3) + (total_output / 1_000_000 * 15)

        # Final summary
        print_header("✅ 완료!")

        print("📊 처리 결과:")
        print(f"   - 인터뷰: {transcript.title}")
        print(f"   - 시간: {transcript.duration_formatted}")
        print(f"   - 섹션: {len(sections)}개")
        print(f"   - 생성 문서: 완전한 분석 보고서")
        print()

        print("💰 비용:")
        print(f"   - 입력 토큰: {total_input:,}")
        print(f"   - 출력 토큰: {total_output:,}")
        print(f"   - 총 비용: ${cost:.2f}")
        print()

        print("📁 생성된 파일:")
        print(f"   - {complete_path}")
        print(f"   - {sections_dir}/ (섹션별 파일)")
        print()

        print("=" * 80)
        print()
        print("🎉 성공!")
        print()
        print(f"📄 결과 확인:")
        print(f"   open {complete_path}")
        print()
        print(f"   또는")
        print(f"   cat {complete_path}")
        print()
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 중단했습니다.")
        sys.exit(1)

    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("💡 문제 해결:")
        print("   1. .env 파일에 API 키가 올바르게 설정되어 있는지 확인")
        print("   2. 인터넷 연결 확인")
        print("   3. Anthropic API 크레딧 확인: https://console.anthropic.com/")
        print()
        sys.exit(1)


if __name__ == '__main__':
    main()
