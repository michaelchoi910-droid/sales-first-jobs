#!/usr/bin/env python3
"""
Quick start example - Process a transcript with minimal configuration
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fireflies_client import FirefliesClient
from src.transcript_processor import TranscriptProcessor
from src.claude_processor import ClaudeProcessor


def main():
    # Load environment variables
    load_dotenv()

    print("🎙️  Quick Start Example")
    print("=" * 80)
    print()

    # Get transcript ID from user
    transcript_id = input("Enter Fireflies transcript ID: ").strip()

    if not transcript_id:
        print("❌ No transcript ID provided")
        return

    try:
        # Step 1: Fetch transcript
        print("\n📥 Fetching transcript...")
        fireflies = FirefliesClient()
        transcript = fireflies.get_transcript(transcript_id)
        print(f"✅ Fetched: {transcript.title}")

        # Step 2: Split into sections
        print("\n✂️  Splitting into sections...")
        processor = TranscriptProcessor(max_tokens_per_section=4000)
        sections = processor.split_by_tokens(transcript)
        print(f"✅ Created {len(sections)} sections")

        # Step 3: Process first section only (for demo)
        print("\n🤖 Processing first section (demo)...")
        claude = ClaudeProcessor()

        processed = claude.process_section(
            sections[0],
            interview_title=transcript.title,
            interview_date=transcript.date.strftime('%Y-%m-%d')
        )

        # Step 4: Display result
        print("\n📄 Result Preview:")
        print("=" * 80)
        print(processed.analysis[:500] + "...")
        print("=" * 80)

        # Step 5: Save
        output_file = f"output_section1_{transcript_id}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {processed.section_title}\n\n")
            f.write(processed.analysis)

        print(f"\n✅ Saved to: {output_file}")
        print()
        print("To process all sections, use: python src/main.py")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
