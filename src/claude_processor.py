"""Process transcript sections using Claude API"""

import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from anthropic import Anthropic
import time

from src.transcript_processor import TranscriptSection
from config.prompts import SECTION_ANALYSIS_PROMPT, FINAL_SYNTHESIS_PROMPT


@dataclass
class ProcessedSection:
    """A processed section with Claude's analysis"""
    section_number: int
    section_title: str
    start_time: str
    end_time: str
    duration: str
    analysis: str  # The detailed analysis from Claude
    token_usage: Dict[str, int]  # Input and output tokens used


class ClaudeProcessor:
    """Process transcript sections using Claude API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-7-sonnet-20250219",
        max_tokens: int = 16000
    ):
        """
        Initialize Claude processor

        Args:
            api_key: Anthropic API key. If None, will try to get from ANTHROPIC_API_KEY env var
            model: Claude model to use (default: Claude 3.5 Sonnet)
            max_tokens: Maximum tokens for Claude's response
        """
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def process_section(
        self,
        section: TranscriptSection,
        interview_title: str,
        interview_date: str,
        retry_count: int = 3
    ) -> ProcessedSection:
        """
        Process a single transcript section with Claude

        Args:
            section: The transcript section to process
            interview_title: Title of the full interview
            interview_date: Date of the interview
            retry_count: Number of retries on failure

        Returns:
            ProcessedSection with detailed analysis
        """
        print(f"\n🔄 Processing Section {section.section_number}: {section.title}")
        print(f"   Tokens: {section.token_count:,} | Time: {section.start_time_formatted} - {section.end_time_formatted}")

        # Prepare the prompt
        prompt = SECTION_ANALYSIS_PROMPT.format(
            interview_title=interview_title,
            interview_date=interview_date,
            section_title=section.title,
            start_time=section.start_time_formatted,
            end_time=section.end_time_formatted,
            duration=section.duration_formatted,
            transcript_text=section.get_text()
        )

        # Process with Claude with retry logic
        for attempt in range(retry_count):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )

                analysis = response.content[0].text

                token_usage = {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }

                print(f"   ✅ Completed! Output: {token_usage['output_tokens']:,} tokens")

                return ProcessedSection(
                    section_number=section.section_number,
                    section_title=section.title,
                    start_time=section.start_time_formatted,
                    end_time=section.end_time_formatted,
                    duration=section.duration_formatted,
                    analysis=analysis,
                    token_usage=token_usage
                )

            except Exception as e:
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"   ⚠️  Error (attempt {attempt + 1}/{retry_count}): {e}")
                    print(f"   Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"   ❌ Failed after {retry_count} attempts: {e}")
                    raise

    def process_all_sections(
        self,
        sections: List[TranscriptSection],
        interview_title: str,
        interview_date: str,
        progress_callback: Optional[callable] = None
    ) -> List[ProcessedSection]:
        """
        Process all transcript sections

        Args:
            sections: List of transcript sections
            interview_title: Title of the full interview
            interview_date: Date of the interview
            progress_callback: Optional callback function(section_num, total) for progress updates

        Returns:
            List of processed sections
        """
        print(f"\n{'='*80}")
        print(f"🚀 Starting processing of {len(sections)} sections")
        print(f"{'='*80}\n")

        processed_sections = []
        total_input_tokens = 0
        total_output_tokens = 0

        for i, section in enumerate(sections, 1):
            processed = self.process_section(section, interview_title, interview_date)
            processed_sections.append(processed)

            total_input_tokens += processed.token_usage["input_tokens"]
            total_output_tokens += processed.token_usage["output_tokens"]

            if progress_callback:
                progress_callback(i, len(sections))

            # Small delay to avoid rate limits
            if i < len(sections):
                time.sleep(1)

        print(f"\n{'='*80}")
        print(f"✅ All sections processed successfully!")
        print(f"{'='*80}")
        print(f"Total input tokens: {total_input_tokens:,}")
        print(f"Total output tokens: {total_output_tokens:,}")
        print(f"Total tokens: {total_input_tokens + total_output_tokens:,}")
        print(f"{'='*80}\n")

        return processed_sections

    def synthesize_final_document(
        self,
        processed_sections: List[ProcessedSection],
        interview_title: str,
        interview_date: str,
        total_duration: str,
        participants: List[str]
    ) -> str:
        """
        Synthesize all processed sections into a final comprehensive document

        Args:
            processed_sections: All processed sections
            interview_title: Title of the interview
            interview_date: Date of the interview
            total_duration: Total interview duration
            participants: List of interview participants

        Returns:
            Final synthesized document
        """
        print(f"\n{'='*80}")
        print(f"🔄 Synthesizing final document...")
        print(f"{'='*80}\n")

        # Create a summary of all sections
        sections_summary = []
        for ps in processed_sections:
            sections_summary.append(
                f"## {ps.section_title}\n"
                f"**시간**: {ps.start_time} - {ps.end_time} ({ps.duration})\n\n"
                f"{ps.analysis}\n\n"
                f"---\n"
            )

        sections_summary_text = "\n".join(sections_summary)

        # Prepare the synthesis prompt
        prompt = FINAL_SYNTHESIS_PROMPT.format(
            interview_title=interview_title,
            interview_date=interview_date,
            total_duration=total_duration,
            participants=", ".join(participants),
            sections_summary=sections_summary_text
        )

        # Generate final document
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            final_document = response.content[0].text

            print(f"✅ Final document synthesized!")
            print(f"   Output: {response.usage.output_tokens:,} tokens")
            print(f"{'='*80}\n")

            return final_document

        except Exception as e:
            print(f"❌ Failed to synthesize final document: {e}")
            raise

    def create_complete_document(
        self,
        processed_sections: List[ProcessedSection],
        final_synthesis: str,
        interview_title: str,
        interview_date: str
    ) -> str:
        """
        Create the complete document combining synthesis and all section details

        Args:
            processed_sections: All processed sections
            final_synthesis: The synthesized final document
            interview_title: Title of the interview
            interview_date: Date of the interview

        Returns:
            Complete document as markdown string
        """
        document_parts = [
            f"# {interview_title}",
            f"**날짜**: {interview_date}\n",
            "---\n",
            final_synthesis,
            "\n\n---\n\n",
            "# 섹션별 상세 분석\n",
            "아래는 각 섹션의 상세 분석 내용입니다.\n"
        ]

        for ps in processed_sections:
            document_parts.append(
                f"\n---\n\n"
                f"# {ps.section_title}\n"
                f"**시간**: {ps.start_time} - {ps.end_time} ({ps.duration})\n\n"
                f"{ps.analysis}\n"
            )

        return "\n".join(document_parts)

    def save_document(self, document: str, output_path: str):
        """
        Save the document to a file

        Args:
            document: The document content
            output_path: Path to save the document
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(document)

        print(f"📄 Document saved to: {output_path}")

    def save_sections_separately(
        self,
        processed_sections: List[ProcessedSection],
        output_dir: str,
        interview_title: str
    ):
        """
        Save each section as a separate file

        Args:
            processed_sections: All processed sections
            output_dir: Directory to save sections
            interview_title: Title of the interview
        """
        os.makedirs(output_dir, exist_ok=True)

        for ps in processed_sections:
            filename = f"section_{ps.section_number:02d}.md"
            filepath = os.path.join(output_dir, filename)

            content = (
                f"# {ps.section_title}\n"
                f"**인터뷰**: {interview_title}\n"
                f"**시간**: {ps.start_time} - {ps.end_time} ({ps.duration})\n\n"
                f"---\n\n"
                f"{ps.analysis}\n"
            )

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

        print(f"📁 {len(processed_sections)} sections saved to: {output_dir}")
