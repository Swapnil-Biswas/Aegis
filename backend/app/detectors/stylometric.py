"""
Module B: Stylometric Fingerprinting.
Analyzes syntactic complexity, function-word distributions, punctuation entropy,
active vs. passive voice, contraction density, transition word usage,
and sentence-opening diversity to identify suspicious uniformity.
"""

import math
import re
from collections import Counter
from typing import Dict, List, Any, Set
import numpy as np

from app.core.preprocessor import PreprocessedDocument, PassageChunk, TextSpan
from app.detectors.base import BaseDetector, DetectorOutput, PassageScore


class StylometricFingerprintDetector(BaseDetector):
    """
    Forensic stylometry engine.
    Extracts authorial habits, syntactic profiles, and punctuation patterns.
    Flags artificial stylistic uniformity without assuming polished prose is synthetic.
    """

    def __init__(self, weight: float = 1.0):
        super().__init__(
            name="stylometric_fingerprinting",
            display_name="Stylometric Fingerprinting",
            weight=weight
        )

        # Standard English function words categories
        self._pronouns: Set[str] = {
            "i", "you", "he", "she", "it", "we", "they", "me", "him", "her",
            "us", "them", "my", "your", "his", "her", "its", "our", "their",
            "mine", "yours", "hers", "ours", "theirs", "myself", "yourself",
            "himself", "herself", "itself", "ourselves", "themselves"
        }
        self._prepositions: Set[str] = {
            "about", "above", "across", "after", "against", "along", "among",
            "around", "at", "before", "behind", "below", "beneath", "beside",
            "between", "beyond", "by", "down", "during", "except", "for",
            "from", "in", "inside", "into", "near", "of", "off", "on", "onto",
            "out", "outside", "over", "past", "through", "throughout", "to",
            "toward", "under", "underneath", "until", "up", "upon", "with",
            "within", "without"
        }
        self._conjunctions: Set[str] = {
            "and", "but", "or", "nor", "for", "yet", "so", "although", "because",
            "since", "unless", "while", "whereas", "whether", "as", "if", "though"
        }
        self._auxiliaries: Set[str] = {
            "is", "am", "are", "was", "were", "be", "being", "been", "have",
            "has", "had", "do", "does", "did", "can", "could", "will", "would",
            "shall", "should", "may", "might", "must"
        }
        self._transitions: Set[str] = {
            "furthermore", "moreover", "consequently", "nevertheless", "nonetheless",
            "additionally", "subsequently", "accordingly", "therefore", "thus",
            "hence", "meanwhile", "alternatively", "specifically", "conversely",
            "ultimately", "importantly", "notably", "significantly"
        }

        # Contraction patterns
        self._contraction_regex = re.compile(
            r"\b[a-zA-Z]+('t|'ve|'re|'ll|'d|'m|’t|’ve|’re|’ll|’d|’m)\b",
            re.IGNORECASE
        )

        # Passive voice pattern: form of 'be' + past participle (approximated with common -ed / irregular forms)
        self._passive_regex = re.compile(
            r"\b(am|is|are|was|were|be|been|being)\s+([a-zA-Z]+ed|written|made|done|seen|given|found|taken|known|held)\b",
            re.IGNORECASE
        )

    def _extract_punctuation_stats(self, text: str) -> Dict[str, float]:
        """Calculates punctuation frequencies and Shannon entropy."""
        punct_marks = [',', ';', ':', '-', '—', '(', ')', '!', '?', '"']
        counts = {p: text.count(p) for p in punct_marks}
        total_punct = sum(counts.values())

        if total_punct == 0:
            return {
                "total_punctuation_count": 0.0,
                "comma_frequency": 0.0,
                "semicolon_frequency": 0.0,
                "emdash_frequency": 0.0,
                "punctuation_entropy": 0.0
            }

        entropy = 0.0
        for cnt in counts.values():
            if cnt > 0:
                p = cnt / total_punct
                entropy -= p * math.log2(p)

        n_chars = max(1, len(text))
        return {
            "total_punctuation_count": float(total_punct),
            "comma_frequency": round(counts[','] / n_chars * 1000, 2),
            "semicolon_frequency": round(counts[';'] / n_chars * 1000, 2),
            "emdash_frequency": round((counts['-'] + counts['—']) / n_chars * 1000, 2),
            "punctuation_entropy": round(float(entropy), 4)
        }

    def _extract_function_words(self, tokens: List[str]) -> Dict[str, float]:
        """Calculates relative frequencies of syntactic function word categories."""
        total = max(1, len(tokens))
        pronoun_count = sum(1 for t in tokens if t in self._pronouns)
        prep_count = sum(1 for t in tokens if t in self._prepositions)
        conj_count = sum(1 for t in tokens if t in self._conjunctions)
        aux_count = sum(1 for t in tokens if t in self._auxiliaries)
        trans_count = sum(1 for t in tokens if t in self._transitions)

        return {
            "pronoun_ratio": round(pronoun_count / total, 4),
            "preposition_ratio": round(prep_count / total, 4),
            "conjunction_ratio": round(conj_count / total, 4),
            "auxiliary_ratio": round(aux_count / total, 4),
            "formal_transition_ratio": round(trans_count / total, 4)
        }

    def _extract_sentence_openings(self, sentences: List[TextSpan]) -> Dict[str, float]:
        """
        Measures diversity of sentence-opening words.
        AI text frequently starts sentences with repetitive structures:
        'The...', 'In...', 'This...', 'Moreover...'.
        """
        if not sentences:
            return {"opening_entropy": 0.0, "opening_uniqueness": 0.0}

        openings = []
        for s in sentences:
            words = re.findall(r'\b[a-zA-Z]+\b', s.text.lower())
            if words:
                openings.append(words[0])

        if not openings:
            return {"opening_entropy": 0.0, "opening_uniqueness": 0.0}

        counts = Counter(openings)
        n = len(openings)
        entropy = 0.0
        for cnt in counts.values():
            p = cnt / n
            entropy -= p * math.log2(p)

        uniqueness = len(counts) / n

        return {
            "opening_entropy": round(float(entropy), 4),
            "opening_uniqueness": round(float(uniqueness), 4)
        }

    def _extract_voice_and_contractions(self, text: str, total_words: int) -> Dict[str, float]:
        """Extracts passive constructions and contraction frequencies."""
        contractions = self._contraction_regex.findall(text)
        passives = self._passive_regex.findall(text)

        w = max(1, total_words)
        return {
            "contraction_count": float(len(contractions)),
            "contraction_density": round((len(contractions) / w) * 100.0, 3),
            "passive_voice_count": float(len(passives)),
            "passive_voice_density": round((len(passives) / w) * 100.0, 3)
        }

    def _extract_clause_complexity(self, sentences: List[TextSpan]) -> Dict[str, float]:
        """
        Estimates subordinate clause complexity via subordinating marker frequencies
        (e.g., that, which, who, where, when, although, because).
        """
        if not sentences:
            return {"clause_complexity_index": 0.0}

        markers = {"that", "which", "who", "whom", "whose", "where", "when", "although", "because", "since", "while"}
        clause_counts = []
        for s in sentences:
            words = re.findall(r'\b[a-zA-Z]+\b', s.text.lower())
            count = sum(1 for w in words if w in markers)
            clause_counts.append(count)

        avg_clauses = float(np.mean(clause_counts)) if clause_counts else 0.0
        return {
            "clause_complexity_index": round(avg_clauses, 3)
        }

    def analyze(self, doc: PreprocessedDocument) -> DetectorOutput:
        tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_\'-]+\b', doc.sanitized_text)]
        n_tokens = len(tokens)

        if n_tokens < 15:
            return DetectorOutput(
                module_name=self.name,
                display_name=self.display_name,
                raw_score=0.5,
                calibrated_score=0.5,
                confidence=0.1,
                observations=["Insufficient words to compute reliable stylometric fingerprints."],
                features={"word_count": float(n_tokens)}
            )

        # 1. Feature computation
        punct_stats = self._extract_punctuation_stats(doc.sanitized_text)
        func_stats = self._extract_function_words(tokens)
        open_stats = self._extract_sentence_openings(doc.sentences)
        voice_stats = self._extract_voice_and_contractions(doc.sanitized_text, n_tokens)
        clause_stats = self._extract_clause_complexity(doc.sentences)

        features: Dict[str, float] = {
            **punct_stats,
            **func_stats,
            **open_stats,
            **voice_stats,
            **clause_stats
        }

        # 2. Heuristic and statistical scoring
        # Typical AI stylometric markers:
        # - Extremely high formal transition frequency (> 0.015 of tokens)
        # - Extremely low contraction density (< 0.2% in informal/balanced text)
        # - Low sentence-opening uniqueness / entropy (repetitive clause starter templates)
        # - Overly uniform punctuation distributions (high comma, absence of dashes/colons)
        #
        # Typical Human stylometric markers:
        # - Dynamic punctuation entropy (dashes, parentheses, conversational cadence)
        # - Diverse sentence-opening distribution (gerunds, prepositional phrases)
        # - Higher contraction usage in general writing

        ai_score = 0.0
        weights = 0.0

        # Transition word density (weight: 2.0)
        tr = func_stats["formal_transition_ratio"]
        if tr > 0.018:
            ai_score += 2.0 * 0.85
        elif tr > 0.010:
            ai_score += 2.0 * 0.65
        elif tr < 0.003:
            ai_score += 2.0 * 0.30
        else:
            ai_score += 2.0 * 0.45
        weights += 2.0

        # Sentence-opening uniqueness (weight: 1.5)
        op_u = open_stats["opening_uniqueness"]
        if op_u < 0.40 and len(doc.sentences) >= 5:
            ai_score += 1.5 * 0.80
        elif op_u > 0.70 and len(doc.sentences) >= 8:
            ai_score += 1.5 * 0.25
        else:
            ai_score += 1.5 * 0.50
        weights += 1.5

        # Punctuation entropy (weight: 1.2)
        pe = punct_stats["punctuation_entropy"]
        if pe < 1.0 and punct_stats["total_punctuation_count"] > 10:
            ai_score += 1.2 * 0.75
        elif pe > 1.8:
            ai_score += 1.2 * 0.25
        else:
            ai_score += 1.2 * 0.50
        weights += 1.2

        # Contraction density (weight: 1.0)
        cd = voice_stats["contraction_density"]
        if cd == 0.0 and n_tokens > 120:
            ai_score += 1.0 * 0.68  # Common in default LLM outputs, but caution: formal academic also lacks contractions
        elif cd > 1.2:
            ai_score += 1.0 * 0.20
        else:
            ai_score += 1.0 * 0.45
        weights += 1.0

        raw_score = ai_score / weights
        calibrated_score = 1.0 / (1.0 + math.exp(-3.8 * (raw_score - 0.50)))

        confidence = 0.3 if n_tokens < 60 else (0.65 if n_tokens < 180 else 0.88)

        # 3. Observations and Contradictions
        observations: List[str] = []
        contradictions: List[str] = []

        if func_stats["formal_transition_ratio"] > 0.015:
            observations.append(
                f"Elevated formal transition marker density ({func_stats['formal_transition_ratio']:.2%}); "
                "prose exhibits frequent rhetorical signposting ('furthermore', 'moreover', 'consequently')."
            )
        if open_stats["opening_uniqueness"] < 0.45 and len(doc.sentences) >= 6:
            observations.append(
                f"Sentence opening diversity is low ({open_stats['opening_uniqueness']:.1%}), showing formulaic syntactic starts."
            )
        if voice_stats["contraction_density"] == 0.0 and n_tokens > 150:
            observations.append("Complete absence of grammatical contractions observed.")

        # Contradictions
        if voice_stats["contraction_density"] > 1.0 and calibrated_score > 0.65:
            contradictions.append(
                "Frequent conversational contractions detected despite formulaic transitions; "
                "suggests human stylistic editing or a conversational prompt persona."
            )
        if punct_stats["emdash_frequency"] > 3.0 and calibrated_score > 0.65:
            contradictions.append(
                "High em-dash punctuation density is typical of expressive human writing, contrasting with AI markers."
            )

        # 4. Passage scores
        passage_scores: List[PassageScore] = []
        for p in doc.passages:
            p_tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_\'-]+\b', p.text)]
            if len(p_tokens) >= 20:
                p_trans = sum(1 for t in p_tokens if t in self._transitions) / len(p_tokens)
                p_contra = len(self._contraction_regex.findall(p.text))
                p_val = 0.5
                if p_trans > 0.018 and p_contra == 0:
                    p_val = 0.75
                elif p_contra > 1 or p_trans < 0.005:
                    p_val = 0.28

                passage_scores.append(
                    PassageScore(
                        passage_id=p.passage_id,
                        index=p.index,
                        score=round(p_val, 3),
                        confidence=round(confidence * 0.9, 3),
                        key_signals={
                            "transition_ratio": round(p_trans, 4),
                            "contractions": p_contra
                        },
                        summary=f"Transitions={p_trans:.2%}, Contractions={p_contra}"
                    )
                )

        return DetectorOutput(
            module_name=self.name,
            display_name=self.display_name,
            raw_score=round(float(raw_score), 4),
            calibrated_score=round(float(calibrated_score), 4),
            confidence=round(float(confidence), 3),
            features=features,
            observations=observations,
            contradictions=contradictions,
            passage_scores=passage_scores
        )
