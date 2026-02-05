#!/usr/bin/env python3
"""
Main workflow script for processing interview transcripts

This script orchestrates the entire workflow:
1. Fetch transcript from Fireflies
2. Split into manageable sections
3. Process each section with Claude
4. Synthesize final document
5. Upload to Google Docs
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

from src.fireflies_client import FirefliesClient
from src.transcript_processor import TranscriptProcessor
from src.claude_processor import ClaudeProcessor
from src.google_docs_client import GoogleDocsClient, setup_google_credentials


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")


def print_step(step_num: int, total_steps: int, description: str):
    """Print a step indicator"""
    print(f"\n[Step {step_num}/{total_steps}] {description}")
    print("-" * 80)


def main():
    """Main workflow"""
    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Process interview transcripts and create detailed analysis documents"
    )
    parser.add_argument(
        '--transcript-id',
        type=str,
        help='Fireflies transcript ID to process'
    )
    parser.add_argument(
        '--list-transcripts',
        action='store_true',
        help='List recent transcripts from Fireflies'
    )
    parser.add_argument(
        '--search',
        type=str,
        help='Search for transcripts by keyword'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./output',
        help='Output directory for generated documents (default: ./output)'
    )
    parser.add_argument(
        '--no-google-docs',
        action='store_true',
        help='Skip Google Docs upload, only save locally'
    )
    parser.add_argument(
        '--split-method',
        type=str,
        choices=['time', 'tokens', 'topics'],
        default='topics',
        help='Method to split transcript (default: topics)'
    )
    parser.add_argument(
        '--max-tokens',
        type=int,
        default=4000,
        help='Maximum tokens per section (default: 4000)'
    )
    parser.add_argument(
        '--setup-google',
        action='store_true',
        help='Show instructions for setting up Google credentials'
    )

    args = parser.parse_args()

    # Show Google setup instructions
    if args.setup_google:
        setup_google_credentials()
        return

    print_header("🎙️  Interview Transcription Summary System")
    print("Context Window 한계를 극복하는 인터뷰 분석 자동화 시스템\n")

    # Initialize clients
    try:
        print("🔧 Initializing API clients...")
        fireflies = FirefliesClient()
        processor = TranscriptProcessor(max_tokens_per_section=args.max_tokens)
        claude = ClaudeProcessor()

        google_docs = None
        if not args.no_google_docs:
            try:
                google_docs = GoogleDocsClient()
                print("✅ All clients initialized successfully\n")
            except (ValueError, FileNotFoundError) as e:
                print(f"⚠️  Google Docs client not available: {e}")
                print("   Continuing without Google Docs upload...\n")

    except Exception as e:
        print(f"❌ Error initializing clients: {e}")
        print("\nPlease check your environment variables:")
        print("  - FIREFLIES_API_KEY")
        print("  - ANTHROPIC_API_KEY")
        print("  - GOOGLE_CREDENTIALS_PATH (optional)")
        sys.exit(1)

    # List transcripts
    if args.list_transcripts:
        print_step(1, 1, "📋 Listing Recent Transcripts")
        try:
            transcripts = fireflies.list_recent_transcripts(limit=20)
            print(f"\nFound {len(transcripts)} recent transcripts:\n")

            for i, t in enumerate(transcripts, 1):
                duration = t.get('duration', 0)
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                print(f"{i:2d}. [{t['id']}]")
                print(f"    Title: {t['title']}")
                print(f"    Date: {t.get('date', 'N/A')}")
                print(f"    Duration: {hours:02d}:{minutes:02d}:00")
                print()

        except Exception as e:
            print(f"❌ Error listing transcripts: {e}")
            sys.exit(1)
        return

    # Search transcripts
    if args.search:
        print_step(1, 1, f"🔍 Searching for: '{args.search}'")
        try:
            transcripts = fireflies.search_transcripts(args.search, limit=20)
            print(f"\nFound {len(transcripts)} matching transcripts:\n")

            for i, t in enumerate(transcripts, 1):
                duration = t.get('duration', 0)
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                print(f"{i:2d}. [{t['id']}]")
                print(f"    Title: {t['title']}")
                print(f"    Date: {t.get('date', 'N/A')}")
                print(f"    Duration: {hours:02d}:{minutes:02d}:00")
                print()

        except Exception as e:
            print(f"❌ Error searching transcripts: {e}")
            sys.exit(1)
        return

    # Get transcript ID
    transcript_id = args.transcript_id
    if not transcript_id:
        # Interactive mode
        print("No transcript ID provided. Enter a transcript ID or search term:")
        print("  - Enter transcript ID directly")
        print("  - Or type 'list' to see recent transcripts")
        print("  - Or type 'search <term>' to search")
        print()

        user_input = input("Enter your choice: ").strip()

        if user_input.lower() == 'list':
            transcripts = fireflies.list_recent_transcripts(limit=20)
            print(f"\nRecent transcripts:\n")

            for i, t in enumerate(transcripts, 1):
                print(f"{i:2d}. [{t['id']}] {t['title']}")

            selection = input("\nSelect a transcript number (or enter ID): ").strip()

            try:
                idx = int(selection) - 1
                if 0 <= idx < len(transcripts):
                    transcript_id = transcripts[idx]['id']
                else:
                    print("Invalid selection")
                    sys.exit(1)
            except ValueError:
                transcript_id = selection

        elif user_input.lower().startswith('search '):
            search_term = user_input[7:].strip()
            transcripts = fireflies.search_transcripts(search_term, limit=20)
            print(f"\nSearch results for '{search_term}':\n")

            for i, t in enumerate(transcripts, 1):
                print(f"{i:2d}. [{t['id']}] {t['title']}")

            selection = input("\nSelect a transcript number (or enter ID): ").strip()

            try:
                idx = int(selection) - 1
                if 0 <= idx < len(transcripts):
                    transcript_id = transcripts[idx]['id']
                else:
                    print("Invalid selection")
                    sys.exit(1)
            except ValueError:
                transcript_id = selection

        else:
            transcript_id = user_input

    if not transcript_id:
        print("❌ No transcript ID provided")
        sys.exit(1)

    # Main processing workflow
    TOTAL_STEPS = 6

    # Step 1: Fetch transcript
    print_step(1, TOTAL_STEPS, "📥 Fetching Transcript from Fireflies")
    try:
        transcript = fireflies.get_transcript(transcript_id)
        print(f"\n✅ Transcript fetched successfully!")
        print(f"   Title: {transcript.title}")
        print(f"   Date: {transcript.date.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Duration: {transcript.duration_formatted}")
        print(f"   Sentences: {len(transcript.sentences):,}")
        print(f"   Participants: {', '.join(transcript.participants)}")

    except Exception as e:
        print(f"❌ Error fetching transcript: {e}")
        sys.exit(1)

    # Step 2: Split transcript into sections
    print_step(2, TOTAL_STEPS, "✂️  Splitting Transcript into Sections")
    try:
        if args.split_method == 'time':
            sections = processor.split_by_time(transcript, time_chunk_minutes=30)
        elif args.split_method == 'tokens':
            sections = processor.split_by_tokens(transcript, max_tokens=args.max_tokens)
        else:  # topics
            sections = processor.split_with_topic_detection(
                transcript,
                min_section_minutes=15,
                max_tokens=args.max_tokens
            )

        print(f"\n{processor.get_section_summary(sections)}")

    except Exception as e:
        print(f"❌ Error splitting transcript: {e}")
        sys.exit(1)

    # Step 3: Process sections with Claude
    print_step(3, TOTAL_STEPS, "🤖 Processing Sections with Claude API")
    try:
        processed_sections = claude.process_all_sections(
            sections,
            interview_title=transcript.title,
            interview_date=transcript.date.strftime('%Y-%m-%d')
        )

    except Exception as e:
        print(f"❌ Error processing sections: {e}")
        sys.exit(1)

    # Step 4: Synthesize final document
    print_step(4, TOTAL_STEPS, "📝 Synthesizing Final Document")
    try:
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

    except Exception as e:
        print(f"❌ Error synthesizing document: {e}")
        sys.exit(1)

    # Step 5: Save locally
    print_step(5, TOTAL_STEPS, "💾 Saving Documents Locally")
    try:
        # Create output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_subdir = os.path.join(
            args.output_dir,
            f"{timestamp}_{transcript_id}"
        )
        os.makedirs(output_subdir, exist_ok=True)

        # Save complete document
        complete_doc_path = os.path.join(output_subdir, "complete_analysis.md")
        claude.save_document(complete_document, complete_doc_path)

        # Save sections separately
        sections_dir = os.path.join(output_subdir, "sections")
        claude.save_sections_separately(
            processed_sections,
            sections_dir,
            transcript.title
        )

        print(f"\n✅ All documents saved to: {output_subdir}")

    except Exception as e:
        print(f"❌ Error saving documents: {e}")
        sys.exit(1)

    # Step 6: Upload to Google Docs (optional)
    if google_docs and not args.no_google_docs:
        print_step(6, TOTAL_STEPS, "☁️  Uploading to Google Docs")
        try:
            doc_title = f"[Interview Analysis] {transcript.title} - {transcript.date.strftime('%Y-%m-%d')}"
            doc_id, doc_url = google_docs.upload_markdown_document(
                doc_title,
                complete_document
            )

            # Save URL to file
            url_file = os.path.join(output_subdir, "google_docs_url.txt")
            with open(url_file, 'w') as f:
                f.write(f"Document URL: {doc_url}\n")
                f.write(f"Document ID: {doc_id}\n")

            print(f"🔗 Google Docs URL saved to: {url_file}")

        except Exception as e:
            print(f"⚠️  Could not upload to Google Docs: {e}")
            print("   Document is still saved locally")

    # Final summary
    print_header("✅ Processing Complete!")
    print(f"📊 Summary:")
    print(f"   • Interview: {transcript.title}")
    print(f"   • Duration: {transcript.duration_formatted}")
    print(f"   • Sections processed: {len(sections)}")
    print(f"   • Output directory: {output_subdir}")
    if google_docs and not args.no_google_docs:
        print(f"   • Google Docs: {doc_url}")
    print(f"\n{'='*80}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
