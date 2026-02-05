#!/usr/bin/env python3
"""
기존 인터뷰를 "이미 처리됨"으로 표시하는 스크립트
이렇게 하면 기존 파일은 건너뛰고 새 파일만 처리합니다.
"""

import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def mark_existing_as_processed():
    """Mark all existing transcripts as already processed"""
    from src.fireflies_client import FirefliesClient

    print("🔍 Fetching existing transcripts from Fireflies...")

    client = FirefliesClient()
    transcripts = client.list_recent_transcripts(limit=50)  # 최근 50개

    print(f"📋 Found {len(transcripts)} transcripts")
    print()

    # Filter by keyword
    keyword = "세일즈 하이브 인터뷰"
    matching = [t for t in transcripts if keyword in t.get('title', '')]

    print(f"🎯 '{keyword}' 키워드 매칭: {len(matching)}개")
    print()

    if not matching:
        print("✅ 매칭되는 기존 인터뷰가 없습니다.")
        return

    print("기존 인터뷰 목록:")
    for i, t in enumerate(matching, 1):
        print(f"  {i}. {t['title']}")
    print()

    # Ask user
    response = input("이 인터뷰들을 '이미 처리됨'으로 표시할까요? (y/N): ").strip().lower()

    if response != 'y':
        print("❌ 취소되었습니다.")
        return

    # Save to processed list
    processed = []
    for t in matching:
        processed.append({
            'id': t['id'],
            'title': t['title'],
            'processed_at': datetime.now().isoformat(),
            'note': 'Marked as processed by init script (not actually processed)'
        })

    with open('.processed_transcripts.json', 'w') as f:
        json.dump(processed, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 80)
    print(f"✅ {len(matching)}개의 인터뷰가 '이미 처리됨'으로 표시되었습니다.")
    print("=" * 80)
    print()
    print("이제 auto_monitor.py를 실행하면 새 인터뷰만 처리합니다:")
    print("  python3 auto_monitor.py")
    print()

if __name__ == '__main__':
    print("=" * 80)
    print("  기존 인터뷰 스킵 설정")
    print("=" * 80)
    print()
    print("이 스크립트는 기존 인터뷰를 '이미 처리됨'으로 표시합니다.")
    print("이렇게 하면 auto_monitor.py 실행 시 기존 파일을 건너뜁니다.")
    print()

    try:
        mark_existing_as_processed()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
