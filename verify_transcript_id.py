#!/usr/bin/env python3
"""Test specific transcript ID"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_transcript_id(transcript_id):
    """Test if transcript ID is valid"""
    api_key = os.getenv("FIREFLIES_API_KEY")

    print(f"🔍 Testing Transcript ID:")
    print(f"   {transcript_id}")
    print()

    api_url = "https://api.fireflies.ai/graphql"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    query = """
    query Transcript($transcriptId: String!) {
        transcript(id: $transcriptId) {
            id
            title
            date
            duration
            participants
        }
    }
    """

    try:
        response = requests.post(
            api_url,
            json={"query": query, "variables": {"transcriptId": transcript_id}},
            headers=headers,
            timeout=30
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if "errors" in data:
                print(f"❌ GraphQL Error: {data['errors']}")
                return False

            transcript = data.get("data", {}).get("transcript")

            if not transcript:
                print("❌ Transcript not found")
                return False

            print("✅ Valid Transcript ID!\n")
            print("=" * 80)
            print("📄 Transcript Info:")
            print("=" * 80)
            print(f"Title: {transcript.get('title')}")
            print(f"Date: {transcript.get('date')}")

            duration = transcript.get('duration', 0)
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            print(f"Duration: {hours:02d}:{minutes:02d}:00")

            print(f"Participants: {', '.join(transcript.get('participants', []))}")
            print("=" * 80)
            print()

            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 80)
    print("  Fireflies Transcript ID Verification")
    print("=" * 80)
    print()

    # Extract ID from URL
    url = "https://app.fireflies.ai/view/-260202-160214::01KGEVQY174T8VF1AK9R55DE1W?channelSource=all"
    transcript_id = url.split('/view/')[1].split('?')[0]

    print(f"📋 Extracted ID from URL:")
    print(f"   {transcript_id}")
    print()

    is_valid = test_transcript_id(transcript_id)

    if is_valid:
        print("🚀 Ready to process!")
        print()
        print("다음 명령으로 자동 처리를 시작할 수 있습니다:")
        print(f"python run_automation.py")
        print()
        print("또는:")
        print(f"python src/main.py --transcript-id '{transcript_id}'")
