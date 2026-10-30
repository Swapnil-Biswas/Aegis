"""
Text preprocessing and structural decomposition engine.
Provides sentence boundary segmentation, character offset tracking,
sliding-window passage segmentation, and text validation.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field


class TextSpan(BaseModel):
    index: int
    text: str
    start_char: int
    end_char: int
    word_count: int


class PassageChunk(BaseModel):
    passage_id: str
    index: int
    text: str
    start_char: int
    end_char: int
    start_word: int
    end_word: int
    word_count: int
    sentence_indices: List[int] = Field(default_factory=list)


class PreprocessedDocument(BaseModel):
    raw_text: str
    sanitized_text: str
    total_characters: int
    total_words: int
    total_sentences: int
    total_paragraphs: int
    sentences: List[TextSpan]
    paragraphs: List[TextSpan]
    passages: List[PassageChunk]
    has_sufficient_evidence: bool
    insufficiency_reason: Optional[str] = None


class ForensicPreprocessor:
    """
    Forensic text preprocessor ensuring zero loss of positional context.
    Tracks precise byte and character offsets for forensic reproducibility.
    """

    def __init__(
        self,
        min_words_sufficient: int = 60,
        passage_window_words: int = 120,
        passage_stride_words: int = 50,
        min_passage_words: int = 35
    ):
        self.min_words_sufficient = min_words_sufficient
        self.passage_window_words = passage_window_words
        self.passage_stride_words = passage_stride_words
        self.min_passage_words = min_passage_words

        # Sentence splitting pattern
        self._sentence_regex = re.compile(
            r'(?<=[.!?])(?:\s+|\n+)(?=[A-Z0-9"\'“‘])',
            re.UNICODE
        )
        self._abbreviations = {
            "mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.", "vs.", "etc.", "e.g.", "i.e."
        }

    def sanitize(self, text: str) -> str:
        """Removes malicious/invisible unicode characters while preserving semantic text layout."""
        if not text:
            return ""
        # Strip zero-width characters and invisible control codes (often used for adversarial evasion)
        cleaned = re.sub(r'[\u200B-\u200D\uFEFF\u00A0\u200E\u200F]', ' ', text)
        # Normalize carriage returns
        cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
        return cleaned

    def extract_paragraphs(self, text: str) -> List[TextSpan]:
        """Extracts paragraph spans with exact character offsets."""
        paragraphs: List[TextSpan] = []
        if not text:
            return paragraphs

        raw_paras = re.split(r'(\n\s*\n+)', text)
        current_offset = 0
        p_idx = 0

        for chunk in raw_paras:
            if chunk.strip():
                start = text.find(chunk, current_offset)
                if start == -1:
                    start = current_offset
                end = start + len(chunk)
                words = len(chunk.split())
                paragraphs.append(
                    TextSpan(
                        index=p_idx,
                        text=chunk.strip(),
                        start_char=start,
                        end_char=end,
                        word_count=words
                    )
                )
                p_idx += 1
                current_offset = end
            else:
                current_offset += len(chunk)

        return paragraphs

    def extract_sentences(self, text: str) -> List[TextSpan]:
        """
        Segments text into sentences with strict boundary validation
        and exact start/end character offsets.
        """
        sentences: List[TextSpan] = []
        if not text or not text.strip():
            return sentences

        # Fallback to paragraph-level splitting first to preserve structure
        paras = re.split(r'\n+', text)
        curr_offset = 0
        s_idx = 0

        for p in paras:
            if not p.strip():
                curr_offset += len(p) + 1
                continue

            p_start = text.find(p, curr_offset)
            if p_start == -1:
                p_start = curr_offset

            # Split paragraph into sentences and merge abbreviations
            raw_splits = self._sentence_regex.split(p)
            splits: List[str] = []
            for rs in raw_splits:
                if splits and any(splits[-1].lower().rstrip().endswith(abbr) for abbr in self._abbreviations):
                    splits[-1] = splits[-1] + " " + rs
                else:
                    splits.append(rs)
            inner_offset = p_start

            for s in splits:
                s_stripped = s.strip()
                if not s_stripped:
                    continue

                actual_start = text.find(s_stripped, inner_offset)
                if actual_start == -1:
                    actual_start = inner_offset
                actual_end = actual_start + len(s_stripped)
                words = len(s_stripped.split())

                sentences.append(
                    TextSpan(
                        index=s_idx,
                        text=s_stripped,
                        start_char=actual_start,
                        end_char=actual_end,
                        word_count=words
                    )
                )
                s_idx += 1
                inner_offset = actual_end

            curr_offset = p_start + len(p)

        return sentences

    def generate_passages(
        self,
        text: str,
        sentences: List[TextSpan]
    ) -> List[PassageChunk]:
        """
        Generates overlapping semantic sliding-window passages.
        Passages are aligned with sentence boundaries whenever possible
        to avoid fragmenting syntactic structures.
        """
        if not sentences:
            total_words = len(text.split())
            if total_words > 0:
                return [
                    PassageChunk(
                        passage_id="passage_0",
                        index=0,
                        text=text.strip(),
                        start_char=0,
                        end_char=len(text),
                        start_word=0,
                        end_word=total_words,
                        word_count=total_words,
                        sentence_indices=[]
                    )
                ]
            return []

        # If document is short, single passage suffices
        total_doc_words = sum(s.word_count for s in sentences)
        if total_doc_words <= self.passage_window_words:
            return [
                PassageChunk(
                    passage_id="passage_0",
                    index=0,
                    text=text[sentences[0].start_char:sentences[-1].end_char],
                    start_char=sentences[0].start_char,
                    end_char=sentences[-1].end_char,
                    start_word=0,
                    end_word=total_doc_words,
                    word_count=total_doc_words,
                    sentence_indices=list(range(len(sentences)))
                )
            ]

        passages: List[PassageChunk] = []
        n_sentences = len(sentences)
        s_start = 0
        passage_id_counter = 0

        while s_start < n_sentences:
            current_words = 0
            s_end = s_start
            window_sentences: List[int] = []

            # Accumulate sentences until window word count is met
            while s_end < n_sentences and current_words < self.passage_window_words:
                current_words += sentences[s_end].word_count
                window_sentences.append(s_end)
                s_end += 1

            if current_words >= self.min_passage_words or not passages:
                start_c = sentences[window_sentences[0]].start_char
                end_c = sentences[window_sentences[-1]].end_char
                passage_text = text[start_c:end_c]
                
                # Compute cumulative word count indices
                prior_words = sum(sentences[i].word_count for i in range(window_sentences[0]))
                
                passages.append(
                    PassageChunk(
                        passage_id=f"passage_{passage_id_counter}",
                        index=passage_id_counter,
                        text=passage_text,
                        start_char=start_c,
                        end_char=end_c,
                        start_word=prior_words,
                        end_word=prior_words + current_words,
                        word_count=current_words,
                        sentence_indices=window_sentences
                    )
                )
                passage_id_counter += 1

            if s_end >= n_sentences:
                break

            # Calculate stride by stepping forward sentence-by-sentence until stride words are consumed
            stride_accum = 0
            step = 0
            for idx in range(s_start, n_sentences):
                stride_accum += sentences[idx].word_count
                step += 1
                if stride_accum >= self.passage_stride_words:
                    break

            s_start += max(1, step)

        return passages

    def process(self, raw_text: str) -> PreprocessedDocument:
        """Main preprocessing pipeline."""
        sanitized = self.sanitize(raw_text)
        words = sanitized.split()
        total_words = len(words)
        total_chars = len(sanitized)

        paragraphs = self.extract_paragraphs(sanitized)
        sentences = self.extract_sentences(sanitized)
        passages = self.generate_passages(sanitized, sentences)

        has_sufficient = total_words >= self.min_words_sufficient
        insufficiency_reason = None
        if not has_sufficient:
            insufficiency_reason = (
                f"Sample contains only {total_words} word(s). Scientific AI detection requires at least "
                f"{self.min_words_sufficient} words to establish valid statistical confidence intervals."
            )

        return PreprocessedDocument(
            raw_text=raw_text,
            sanitized_text=sanitized,
            total_characters=total_chars,
            total_words=total_words,
            total_sentences=len(sentences),
            total_paragraphs=len(paragraphs),
            sentences=sentences,
            paragraphs=paragraphs,
            passages=passages,
            has_sufficient_evidence=has_sufficient,
            insufficiency_reason=insufficiency_reason
        )
