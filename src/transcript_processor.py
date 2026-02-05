"""Process and segment interview transcripts into manageable sections"""

import os
from typing import List, Dict, Optional
from dataclasses import dataclass
import tiktoken
from anthropic import Anthropic

from src.fireflies_client import TranscriptData, TranscriptSentence, format_time


@dataclass
class TranscriptSection:
    """A section of the transcript"""
    section_number: int
    title: str
    start_time: float
    end_time: float
    sentences: List[TranscriptSentence]
    token_count: int

    @property
    def duration(self) -> float:
        """Duration of this section in seconds"""
        return self.end_time - self.start_time

    @property
    def duration_formatted(self) -> str:
        """Return duration in HH:MM:SS format"""
        return format_time(self.duration)

    @property
    def start_time_formatted(self) -> str:
        """Return start time in HH:MM:SS format"""
        return format_time(self.start_time)

    @property
    def end_time_formatted(self) -> str:
        """Return end time in HH:MM:SS format"""
        return format_time(self.end_time)

    def get_text(self) -> str:
        """Get the full text of this section with speaker labels"""
        lines = []
        current_speaker = None

        for sentence in self.sentences:
            if sentence.speaker_name != current_speaker:
                current_speaker = sentence.speaker_name
                lines.append(f"\n[{current_speaker}] ({format_time(sentence.start_time)})")

            lines.append(sentence.text)

        return " ".join(lines).strip()


class TranscriptProcessor:
    """Process transcripts and split them into manageable sections"""

    def __init__(self, max_tokens_per_section: int = 4000):
        """
        Initialize the processor

        Args:
            max_tokens_per_section: Maximum tokens per section for Claude processing
        """
        self.max_tokens_per_section = max_tokens_per_section
        self.encoding = tiktoken.encoding_for_model("gpt-4")  # Similar tokenization to Claude

        # Initialize Claude client for topic detection
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.claude_client = Anthropic(api_key=api_key) if api_key else None

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))

    def split_by_time(
        self,
        transcript: TranscriptData,
        time_chunk_minutes: int = 30
    ) -> List[TranscriptSection]:
        """
        Split transcript into time-based chunks

        Args:
            transcript: The full transcript
            time_chunk_minutes: Size of each time chunk in minutes

        Returns:
            List of transcript sections
        """
        time_chunk_seconds = time_chunk_minutes * 60
        sections = []
        current_section_sentences = []
        section_start_time = 0
        section_number = 1

        for sentence in transcript.sentences:
            # Check if we should start a new section
            if sentence.start_time >= section_start_time + time_chunk_seconds and current_section_sentences:
                # Create section
                section = self._create_section(
                    section_number=section_number,
                    title=f"Section {section_number} ({format_time(section_start_time)} - {format_time(current_section_sentences[-1].end_time)})",
                    start_time=section_start_time,
                    end_time=current_section_sentences[-1].end_time,
                    sentences=current_section_sentences
                )
                sections.append(section)

                # Start new section
                section_number += 1
                section_start_time = sentence.start_time
                current_section_sentences = []

            current_section_sentences.append(sentence)

        # Add final section
        if current_section_sentences:
            section = self._create_section(
                section_number=section_number,
                title=f"Section {section_number} ({format_time(section_start_time)} - {format_time(current_section_sentences[-1].end_time)})",
                start_time=section_start_time,
                end_time=current_section_sentences[-1].end_time,
                sentences=current_section_sentences
            )
            sections.append(section)

        return sections

    def split_by_tokens(
        self,
        transcript: TranscriptData,
        max_tokens: Optional[int] = None
    ) -> List[TranscriptSection]:
        """
        Split transcript into token-limited chunks

        Args:
            transcript: The full transcript
            max_tokens: Maximum tokens per section (uses default if None)

        Returns:
            List of transcript sections
        """
        max_tokens = max_tokens or self.max_tokens_per_section
        sections = []
        current_section_sentences = []
        current_token_count = 0
        section_number = 1

        for sentence in transcript.sentences:
            sentence_text = f"[{sentence.speaker_name}] {sentence.text}"
            sentence_tokens = self.count_tokens(sentence_text)

            # Check if adding this sentence would exceed token limit
            if current_token_count + sentence_tokens > max_tokens and current_section_sentences:
                # Create section
                section = self._create_section(
                    section_number=section_number,
                    title=f"Section {section_number} ({format_time(current_section_sentences[0].start_time)} - {format_time(current_section_sentences[-1].end_time)})",
                    start_time=current_section_sentences[0].start_time,
                    end_time=current_section_sentences[-1].end_time,
                    sentences=current_section_sentences
                )
                sections.append(section)

                # Start new section
                section_number += 1
                current_section_sentences = []
                current_token_count = 0

            current_section_sentences.append(sentence)
            current_token_count += sentence_tokens

        # Add final section
        if current_section_sentences:
            section = self._create_section(
                section_number=section_number,
                title=f"Section {section_number} ({format_time(current_section_sentences[0].start_time)} - {format_time(current_section_sentences[-1].end_time)})",
                start_time=current_section_sentences[0].start_time,
                end_time=current_section_sentences[-1].end_time,
                sentences=current_section_sentences
            )
            sections.append(section)

        return sections

    def split_with_topic_detection(
        self,
        transcript: TranscriptData,
        min_section_minutes: int = 15,
        max_tokens: Optional[int] = None
    ) -> List[TranscriptSection]:
        """
        Split transcript using Claude to detect topic changes

        This method uses Claude to identify natural topic boundaries in the conversation,
        then creates sections based on those boundaries while respecting token limits.

        Args:
            transcript: The full transcript
            min_section_minutes: Minimum section length in minutes
            max_tokens: Maximum tokens per section

        Returns:
            List of transcript sections with descriptive titles
        """
        if not self.claude_client:
            # Fallback to token-based splitting if Claude is not available
            print("Warning: Claude API not configured, falling back to token-based splitting")
            return self.split_by_tokens(transcript, max_tokens)

        max_tokens = max_tokens or self.max_tokens_per_section
        min_section_seconds = min_section_minutes * 60

        # First, get a rough split by time to make the transcript more manageable
        rough_sections = self.split_by_time(transcript, time_chunk_minutes=min_section_minutes)

        # Use Claude to analyze each rough section and identify topics
        refined_sections = []
        section_number = 1

        for rough_section in rough_sections:
            # Get topic analysis from Claude
            topic_title = self._detect_section_topic(rough_section)

            # Check if section is too large and needs further splitting
            if rough_section.token_count > max_tokens:
                # Split by tokens but preserve the topic info
                subsections = self._split_large_section(
                    rough_section,
                    max_tokens,
                    base_title=topic_title,
                    start_section_number=section_number
                )
                refined_sections.extend(subsections)
                section_number += len(subsections)
            else:
                # Use the section as-is with the detected topic
                section = TranscriptSection(
                    section_number=section_number,
                    title=topic_title,
                    start_time=rough_section.start_time,
                    end_time=rough_section.end_time,
                    sentences=rough_section.sentences,
                    token_count=rough_section.token_count
                )
                refined_sections.append(section)
                section_number += 1

        return refined_sections

    def _detect_section_topic(self, section: TranscriptSection) -> str:
        """Use Claude to detect the main topic of a section"""
        if not self.claude_client:
            return section.title

        # Get a sample of the section (first 1000 tokens to save on API calls)
        section_text = section.get_text()
        tokens = self.encoding.encode(section_text)[:1000]
        sample_text = self.encoding.decode(tokens)

        prompt = f"""다음은 3시간 인터뷰의 일부 transcript입니다.
이 섹션의 주요 주제를 한 문장으로 간결하게 요약해주세요.
한국어로 답변하되, 구체적이고 실용적인 제목을 만들어주세요.

Transcript:
{sample_text}

주제 (한 문장으로):"""

        try:
            response = self.claude_client.messages.create(
                model="claude-3-5-haiku-20241022",  # Use Haiku for cost efficiency
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            topic = response.content[0].text.strip()
            return f"Section {section.section_number}: {topic}"

        except Exception as e:
            print(f"Warning: Failed to detect topic for section {section.section_number}: {e}")
            return section.title

    def _split_large_section(
        self,
        section: TranscriptSection,
        max_tokens: int,
        base_title: str,
        start_section_number: int
    ) -> List[TranscriptSection]:
        """Split a large section into smaller subsections"""
        subsections = []
        current_sentences = []
        current_tokens = 0
        subsection_number = start_section_number

        for sentence in section.sentences:
            sentence_text = f"[{sentence.speaker_name}] {sentence.text}"
            sentence_tokens = self.count_tokens(sentence_text)

            if current_tokens + sentence_tokens > max_tokens and current_sentences:
                # Create subsection
                part_num = subsection_number - start_section_number + 1
                subsection = self._create_section(
                    section_number=subsection_number,
                    title=f"{base_title} (Part {part_num})",
                    start_time=current_sentences[0].start_time,
                    end_time=current_sentences[-1].end_time,
                    sentences=current_sentences
                )
                subsections.append(subsection)

                subsection_number += 1
                current_sentences = []
                current_tokens = 0

            current_sentences.append(sentence)
            current_tokens += sentence_tokens

        # Add final subsection
        if current_sentences:
            part_num = subsection_number - start_section_number + 1
            subsection = self._create_section(
                section_number=subsection_number,
                title=f"{base_title} (Part {part_num})" if len(subsections) > 0 else base_title,
                start_time=current_sentences[0].start_time,
                end_time=current_sentences[-1].end_time,
                sentences=current_sentences
            )
            subsections.append(subsection)

        return subsections

    def _create_section(
        self,
        section_number: int,
        title: str,
        start_time: float,
        end_time: float,
        sentences: List[TranscriptSentence]
    ) -> TranscriptSection:
        """Create a transcript section and calculate its token count"""
        section_text = " ".join([f"[{s.speaker_name}] {s.text}" for s in sentences])
        token_count = self.count_tokens(section_text)

        return TranscriptSection(
            section_number=section_number,
            title=title,
            start_time=start_time,
            end_time=end_time,
            sentences=sentences,
            token_count=token_count
        )

    def get_section_summary(self, sections: List[TranscriptSection]) -> str:
        """Get a summary of all sections"""
        summary_lines = [
            "=" * 80,
            "TRANSCRIPT SECTIONS SUMMARY",
            "=" * 80,
            ""
        ]

        total_tokens = sum(s.token_count for s in sections)

        for section in sections:
            summary_lines.append(
                f"[Section {section.section_number}] {section.title}\n"
                f"  Time: {section.start_time_formatted} - {section.end_time_formatted} "
                f"({section.duration_formatted})\n"
                f"  Tokens: {section.token_count:,}\n"
                f"  Sentences: {len(section.sentences)}\n"
            )

        summary_lines.append("=" * 80)
        summary_lines.append(f"Total Sections: {len(sections)}")
        summary_lines.append(f"Total Tokens: {total_tokens:,}")
        summary_lines.append("=" * 80)

        return "\n".join(summary_lines)
