#!/usr/bin/env python3
"""Quick test script for Fireflies API"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_fireflies():
    """Test Fireflies API connection"""
    api_key = os.getenv("FIREFLIES_API_KEY")

    if not api_key:
        print("❌ No Fireflies API key found")
        return

    print("🔑 Fireflies API key found")
    print(f"   Key: {api_key[:10]}...")

    # Try to fetch recent transcripts
    print("\n📋 Fetching recent transcripts...")

    api_url = "https://api.fireflies.ai/graphql"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    query = """
    query Transcripts($limit: Int!) {
        transcripts(limit: $limit) {
            id
            title
            date
            duration
        }
    }
    """

    try:
        response = requests.post(
            api_url,
            json={"query": query, "variables": {"limit": 10}},
            headers=headers,
            timeout=30
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if "errors" in data:
                print(f"   ❌ GraphQL errors: {data['errors']}")
                return

            transcripts = data.get("data", {}).get("transcripts", [])

            if not transcripts:
                print("   ⚠️  No transcripts found")
                print("\n💡 Tip: Fireflies에 인터뷰 녹음이 있는지 확인해주세요.")
                return

            print(f"   ✅ Found {len(transcripts)} transcripts:\n")

            for i, t in enumerate(transcripts, 1):
                duration = t.get('duration', 0)
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)

                print(f"   {i:2d}. [{t['id'][:20]}...]")
                print(f"       Title: {t['title']}")
                print(f"       Date: {t.get('date', 'N/A')}")
                print(f"       Duration: {hours:02d}:{minutes:02d}:00")
                print()

            # Return first transcript ID for testing
            return transcripts[0]['id']
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == '__main__':
    print("="*80)
    print("  Fireflies API Test")
    print("="*80)

    transcript_id = test_fireflies()

    if transcript_id:
        print(f"\n✅ Test successful!")
        print(f"\n다음 명령으로 이 인터뷰를 처리할 수 있습니다:")
        print(f"   python test_claude_processing.py {transcript_id}")
