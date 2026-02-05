#!/usr/bin/env python3
"""
🤖 완전 자동화 모니터
Fireflies에 새 인터뷰가 업로드되면 자동으로 처리합니다.

사용법:
    python auto_monitor.py

백그라운드 실행:
    nohup python auto_monitor.py > monitor.log 2>&1 &
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()


def load_processed_ids():
    """Load list of already processed transcript IDs"""
    if os.path.exists('.processed_transcripts.json'):
        with open('.processed_transcripts.json', 'r') as f:
            return json.load(f)
    return []


def save_processed_id(transcript_id, title):
    """Save processed transcript ID"""
    processed = load_processed_ids()
    processed.append({
        'id': transcript_id,
        'title': title,
        'processed_at': datetime.now().isoformat()
    })
    with open('.processed_transcripts.json', 'w') as f:
        json.dump(processed, f, indent=2, ensure_ascii=False)


def check_new_transcripts():
    """Check for new transcripts in Fireflies"""
    from src.fireflies_client import FirefliesClient

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Checking for new transcripts...")

    try:
        client = FirefliesClient()
        transcripts = client.list_recent_transcripts(limit=10)

        if not transcripts:
            print("   No transcripts found")
            return []

        # Filter out already processed
        processed_ids = [p['id'] for p in load_processed_ids()]
        new_transcripts = [t for t in transcripts if t['id'] not in processed_ids]

        if new_transcripts:
            print(f"   ✅ Found {len(new_transcripts)} new transcript(s)!")
            for t in new_transcripts:
                duration = t.get('duration', 0)
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                print(f"      - {t['title']} ({hours:02d}:{minutes:02d}:00)")
        else:
            print("   No new transcripts")

        return new_transcripts

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []


def process_transcript(transcript_id, title):
    """Process a single transcript"""
    from src.fireflies_client import FirefliesClient
    from src.transcript_processor import TranscriptProcessor
    from src.claude_processor import ClaudeProcessor
    from src.google_docs_client import GoogleDocsClient

    print()
    print("=" * 80)
    print(f"🚀 Processing: {title}")
    print("=" * 80)
    print()

    try:
        # Step 1: Fetch transcript
        print("[1/5] 📥 Fetching transcript from Fireflies...")
        fireflies = FirefliesClient()
        transcript = fireflies.get_transcript(transcript_id)
        print(f"   ✅ Duration: {transcript.duration_formatted}")
        print(f"   ✅ Sentences: {len(transcript.sentences):,}")

        # Step 2: Split into sections
        print("[2/5] ✂️  Splitting into sections...")
        processor = TranscriptProcessor(max_tokens_per_section=4000)
        sections = processor.split_with_topic_detection(
            transcript,
            min_section_minutes=15,
            max_tokens=4000
        )
        print(f"   ✅ Created {len(sections)} sections")

        # Step 3: Process with Claude
        print("[3/5] 🤖 Processing with Claude API...")
        claude = ClaudeProcessor(
            model="claude-3-7-sonnet-20250219",
            max_tokens=16000
        )
        processed_sections = claude.process_all_sections(
            sections,
            interview_title=transcript.title,
            interview_date=transcript.date.strftime('%Y-%m-%d')
        )

        # Step 4: Synthesize
        print("[4/5] 📝 Creating final document...")
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

        # Step 5: Upload to Google Docs
        print("[5/5] ☁️  Uploading to Google Docs...")

        # Save locally first
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join('output', f"{timestamp}_{transcript_id[:10]}")
        os.makedirs(output_dir, exist_ok=True)

        local_path = os.path.join(output_dir, "complete_analysis.md")
        claude.save_document(complete_document, local_path)
        print(f"   ✅ Saved locally: {local_path}")

        # Upload to Google Docs (if configured)
        try:
            google_docs = GoogleDocsClient()
            doc_title = f"{transcript.title} - {transcript.date.strftime('%Y-%m-%d')}"
            doc_id, doc_url = google_docs.upload_markdown_document(doc_title, complete_document)

            # Save URL
            url_file = os.path.join(output_dir, "google_docs_url.txt")
            with open(url_file, 'w') as f:
                f.write(f"Title: {doc_title}\n")
                f.write(f"URL: {doc_url}\n")
                f.write(f"ID: {doc_id}\n")

            print(f"   ✅ Google Docs: {doc_url}")

        except Exception as e:
            print(f"   ⚠️  Google Docs upload failed: {e}")
            print(f"   Document saved locally only")

        # Mark as processed
        save_processed_id(transcript_id, title)

        print()
        print("=" * 80)
        print(f"✅ Successfully processed: {title}")
        print("=" * 80)
        print()

        return True

    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ Error processing {title}: {e}")
        print("=" * 80)
        print()
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main monitoring loop"""
    print("=" * 80)
    print("  🤖 Fireflies Auto-Monitor")
    print("  자동으로 새 인터뷰를 감지하고 처리합니다")
    print("=" * 80)
    print()
    print("⚙️  설정:")
    print(f"   체크 주기: 5분마다")
    print(f"   Fireflies API: {os.getenv('FIREFLIES_API_KEY')[:10]}...")
    print(f"   Claude API: {os.getenv('ANTHROPIC_API_KEY')[:10]}...")
    print()
    print("💡 종료하려면 Ctrl+C를 누르세요")
    print()
    print("=" * 80)
    print()

    CHECK_INTERVAL = 300  # 5 minutes

    try:
        while True:
            # Check for new transcripts
            new_transcripts = check_new_transcripts()

            # Process each new transcript
            for transcript in new_transcripts:
                success = process_transcript(transcript['id'], transcript['title'])

                if success:
                    print(f"✅ {transcript['title']} 처리 완료!")
                else:
                    print(f"❌ {transcript['title']} 처리 실패")

                # Small delay between transcripts
                time.sleep(10)

            # Wait before next check
            next_check = datetime.now() + timedelta(seconds=CHECK_INTERVAL)
            print(f"⏰ Next check: {next_check.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print()
        print()
        print("=" * 80)
        print("  👋 Monitor stopped by user")
        print("=" * 80)
        print()
        sys.exit(0)

    except Exception as e:
        print()
        print("=" * 80)
        print(f"  ❌ Monitor crashed: {e}")
        print("=" * 80)
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
