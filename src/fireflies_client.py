"""Fireflies.ai API Client for fetching interview transcripts"""

import os
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TranscriptSentence:
    """Individual sentence in the transcript"""
    text: str
    speaker_name: str
    start_time: float  # seconds
    end_time: float    # seconds


@dataclass
class TranscriptData:
    """Complete transcript data from Fireflies"""
    transcript_id: str
    title: str
    date: datetime
    duration: float  # seconds
    sentences: List[TranscriptSentence]
    participants: List[str]

    @property
    def duration_formatted(self) -> str:
        """Return duration in HH:MM:SS format"""
        hours = int(self.duration // 3600)
        minutes = int((self.duration % 3600) // 60)
        seconds = int(self.duration % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class FirefliesClient:
    """Client for interacting with Fireflies.ai API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Fireflies client

        Args:
            api_key: Fireflies API key. If None, will try to get from FIREFLIES_API_KEY env var
        """
        self.api_key = api_key or os.getenv("FIREFLIES_API_KEY")
        if not self.api_key:
            raise ValueError("Fireflies API key is required. Set FIREFLIES_API_KEY environment variable.")

        self.api_url = "https://api.fireflies.ai/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_transcript(self, transcript_id: str) -> TranscriptData:
        """
        Fetch a transcript by ID from Fireflies

        Args:
            transcript_id: The Fireflies transcript ID

        Returns:
            TranscriptData object containing the full transcript
        """
        query = """
        query Transcript($transcriptId: String!) {
            transcript(id: $transcriptId) {
                id
                title
                date
                duration
                sentences {
                    text
                    speaker_name
                    start_time
                    end_time
                }
                participants
            }
        }
        """

        variables = {"transcriptId": transcript_id}

        response = requests.post(
            self.api_url,
            json={"query": query, "variables": variables},
            headers=self.headers,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Failed to fetch transcript: {response.status_code} - {response.text}")

        data = response.json()

        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")

        transcript = data["data"]["transcript"]

        # Parse sentences
        sentences = [
            TranscriptSentence(
                text=s["text"],
                speaker_name=s["speaker_name"],
                start_time=s["start_time"],
                end_time=s["end_time"]
            )
            for s in transcript["sentences"]
        ]

        # Parse date
        try:
            date = datetime.fromisoformat(transcript["date"].replace("Z", "+00:00"))
        except:
            date = datetime.now()

        return TranscriptData(
            transcript_id=transcript["id"],
            title=transcript["title"],
            date=date,
            duration=transcript["duration"],
            sentences=sentences,
            participants=transcript.get("participants", [])
        )

    def list_recent_transcripts(self, limit: int = 10) -> List[Dict]:
        """
        List recent transcripts

        Args:
            limit: Maximum number of transcripts to return

        Returns:
            List of transcript metadata
        """
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

        variables = {"limit": limit}

        response = requests.post(
            self.api_url,
            json={"query": query, "variables": variables},
            headers=self.headers,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Failed to list transcripts: {response.status_code} - {response.text}")

        data = response.json()

        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")

        return data["data"]["transcripts"]

    def search_transcripts(self, search_term: str, limit: int = 10) -> List[Dict]:
        """
        Search for transcripts by title or content

        Args:
            search_term: Term to search for
            limit: Maximum number of results

        Returns:
            List of matching transcript metadata
        """
        query = """
        query SearchTranscripts($searchTerm: String!, $limit: Int!) {
            transcripts(search: $searchTerm, limit: $limit) {
                id
                title
                date
                duration
            }
        }
        """

        variables = {"searchTerm": search_term, "limit": limit}

        response = requests.post(
            self.api_url,
            json={"query": query, "variables": variables},
            headers=self.headers,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Failed to search transcripts: {response.status_code} - {response.text}")

        data = response.json()

        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")

        return data["data"]["transcripts"]


def format_time(seconds: float) -> str:
    """Format seconds as HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
