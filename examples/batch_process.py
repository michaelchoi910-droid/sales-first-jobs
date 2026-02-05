#!/usr/bin/env python3
"""
Batch processing example - Process multiple transcripts at once
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fireflies_client import FirefliesClient
from src.transcript_processor import TranscriptProcessor
from src.claude_processor import ClaudeProcessor


def process_transcript(transcript_id: str, output_base_dir: str):
    """Process a single transcript"""
    try:
        # Initialize clients
        fireflies = FirefliesClient()
        processor = TranscriptProcessor(max_tokens_per_section=4000)
        claude = ClaudeProcessor()

        # Fetch transcript
        print(f"\n📥 Fetching transcript {transcript_id}...")
        transcript = fireflies.get_transcript(transcript_id)
        print(f"   Title: {transcript.title}")

        # Split into sections
        print(f"✂️  Splitting into sections...")
        sections = processor.split_by_tokens(transcript)
        print(f"   Created {len(sections)} sections")

        # Process sections
        print(f"🤖 Processing sections...")
        processed_sections = claude.process_all_sections(
            sections,
            interview_title=transcript.title,
            interview_date=transcript.date.strftime('%Y-%m-%d')
        )

        # Synthesize
        print(f"📝 Synthesizing final document...")
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

        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join(output_base_dir, f"{timestamp}_{transcript_id}")
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "complete_analysis.md")
        claude.save_document(complete_document, output_file)

        print(f"✅ Completed: {transcript.title}")
        print(f"   Saved to: {output_dir}")

        return True

    except Exception as e:
        print(f"❌ Error processing {transcript_id}: {e}")
        return False


def main():
    # Load environment variables
    load_dotenv()

    print("🎙️  Batch Processing Example")
    print("=" * 80)
    print()

    # Get transcript IDs
    print("Enter transcript IDs (one per line, empty line to finish):")
    transcript_ids = []
    while True:
        line = input().strip()
        if not line:
            break
        transcript_ids.append(line)

    if not transcript_ids:
        print("❌ No transcript IDs provided")
        return

    print(f"\n📋 Processing {len(transcript_ids)} transcripts...")
    print("=" * 80)

    # Create output directory
    output_base_dir = "batch_output"
    os.makedirs(output_base_dir, exist_ok=True)

    # Process each transcript
    results = []
    for i, transcript_id in enumerate(transcript_ids, 1):
        print(f"\n[{i}/{len(transcript_ids)}] Processing {transcript_id}")
        print("-" * 80)

        success = process_transcript(transcript_id, output_base_dir)
        results.append((transcript_id, success))

        # Wait between transcripts to avoid rate limits
        if i < len(transcript_ids):
            print("\n⏳ Waiting 5 seconds before next transcript...")
            time.sleep(5)

    # Summary
    print("\n" + "=" * 80)
    print("📊 Batch Processing Summary")
    print("=" * 80)

    successful = sum(1 for _, success in results if success)
    failed = len(results) - successful

    print(f"Total: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\nFailed transcripts:")
        for transcript_id, success in results:
            if not success:
                print(f"  - {transcript_id}")

    print("=" * 80)


if __name__ == '__main__':
    main()
