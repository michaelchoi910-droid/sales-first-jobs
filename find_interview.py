#!/usr/bin/env python3
"""Find specific interview in Fireflies"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def search_fireflies(search_term):
    """Search for transcripts by title"""
    api_key = os.getenv("FIREFLIES_API_KEY")

    print(f"🔍 Searching for: '{search_term}'")
    print()

    api_url = "https://api.fireflies.ai/graphql"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Try listing all recent transcripts first
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
            json={"query": query, "variables": {"limit": 50}},
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            if "errors" in data:
                print(f"❌ Error: {data['errors']}")
                return None

            transcripts = data.get("data", {}).get("transcripts", [])

            if not transcripts:
                print("⚠️  No transcripts found")
                return None

            print(f"✅ Found {len(transcripts)} total transcripts\n")
            print("=" * 80)

            # Search for matching title
            matches = []
            for t in transcripts:
                title = t.get('title', '')
                if search_term.lower() in title.lower():
                    matches.append(t)

            if matches:
                print(f"🎯 Found {len(matches)} match(es) for '{search_term}':\n")

                for i, t in enumerate(matches, 1):
                    duration = t.get('duration', 0)
                    hours = int(duration // 3600)
                    minutes = int((duration % 3600) // 60)

                    print(f"{i}. 📄 {t['title']}")
                    print(f"   ID: {t['id']}")
                    print(f"   Date: {t.get('date', 'N/A')}")
                    print(f"   Duration: {hours:02d}:{minutes:02d}:00")
                    print()

                return matches[0]['id']
            else:
                print(f"⚠️  No exact match found for '{search_term}'")
                print(f"\nShowing all available transcripts:\n")

                for i, t in enumerate(transcripts, 1):
                    duration = t.get('duration', 0)
                    hours = int(duration // 3600)
                    minutes = int((duration % 3600) // 60)

                    print(f"{i:2d}. {t['title']}")
                    print(f"     ID: {t['id']}")
                    print(f"     Duration: {hours:02d}:{minutes:02d}:00")
                    print()

                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == '__main__':
    print("=" * 80)
    print("  Fireflies Interview Search")
    print("=" * 80)
    print()

    transcript_id = search_fireflies("사이드바이사이드 이요한")

    if transcript_id:
        print("=" * 80)
        print(f"✅ Found transcript!")
        print(f"   ID: {transcript_id}")
        print("=" * 80)
        print()
        print("다음 명령으로 자동 처리를 시작할 수 있습니다:")
        print(f"python run_full_automation.py {transcript_id}")
    else:
        print("=" * 80)
        print("⚠️  Target transcript not found")
        print("위 목록에서 원하는 transcript ID를 직접 선택해주세요.")
        print("=" * 80)
