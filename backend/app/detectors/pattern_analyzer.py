"""
Module E: AI Generation Pattern Analysis.
Identifies rhetorical boilerplate, hallmark phrases, formulaic framing,
predictable elaboration templates, and artificial hedging structures.
"""

import math
import re
from typing import Dict, List, Any, Set
from collections import Counter

from app.core.preprocessor import PreprocessedDocument, PassageChunk, TextSpan
from app.detectors.base import BaseDetector, DetectorOutput, PassageScore


class AIPatternDetector(BaseDetector):
    """
    Forensic AI rhetorical pattern engine.
    Detects formulaic syntactic templates, hallmark token n-grams,
    and synthetic structural habits (e.g. 'testament to', 'tapestry of', 'delve into').
    """

    def __init__(self, weight: float = 1.0):
        super().__init__(
            name="pattern_analysis",
            display_name="AI Generation Pattern Analysis",
            weight=weight
        )

        # Empirically validated hallmark n-grams over-represented in LLM outputs
        self._hallmark_phrases: List[re.Pattern] = [
            re.compile(r"\bdelve(?:s|d)?\s+into\b", re.I),
            re.compile(r"\btestament\s+to\b", re.I),
            re.compile(r"\btapestry\s+of\b", re.I),
            re.compile(r"\bfoster(?:s|ing)?\s+a\b", re.I),
            re.compile(r"\bbeacon\s+of\b", re.I),
            re.compile(r"\bvibrant\s+landscape\b", re.I),
            re.compile(r"\binterplay\s+between\b", re.I),
            re.compile(r"\bmultifaceted\b", re.I),
            re.compile(r"\bgame-changer\b", re.I),
            re.compile(r"\bpivotal\s+role\b", re.I),
            re.compile(r"\bindelible\s+mark\b", re.I),
            re.compile(r"\bnuanced\s+understanding\b", re.I),
            re.compile(r"\brealm\s+of\b", re.I),
            re.compile(r"\bharness(?:ing)?\s+the\s+power\b", re.I),
            re.compile(r"\bunwavering\s+commitment\b", re.I),
            re.compile(r"\bever-evolving\b", re.I),
            re.compile(r"\brich\s+history\b", re.I),
        ]

        # Formulaic introductory and conclusion templates
        self._boilerplate_templates: List[re.Pattern] = [
            re.compile(r"\b(?:it\s+is\s+(?:important|worth|crucial|essential)\s+to\s+(?:note|remember|recognize))\b", re.I),
            re.compile(r"\b(?:in\s+today's\s+(?:fast-paced|interconnected|digital)\s+world)\b", re.I),
            re.compile(r"\b(?:in\s+conclusion|to\s+summarize|all\s+in\s+all|in\s+summary|ultimately,\s+it\s+is\s+clear)\b", re.I),
            re.compile(r"\b(?:serves\s+as\s+a\s+(?:stark\s+)?reminder)\b", re.I),
            re.compile(r"\b(?:plays?\s+a\s+crucial\s+role\s+in)\b", re.I),
            re.compile(r"\b(?:not\s+only\s+[^,]+,\s*but\s+also\s+[^.]+)\b", re.I),
        ]

        # Neutral "both sides" artificial hedging patterns
        self._hedging_patterns: List[re.Pattern] = [
            re.compile(r"\bwhile\s+some\s+argue\b.*?\bothers\s+(?:contend|believe|suggest)\b", re.I),
            re.compile(r"\bon\s+one\s+hand\b.*?\bon\s+the\s+other\s+hand\b", re.I),
            re.compile(r"\bit\s+remains\s+to\s+be\s+seen\b", re.I),
            re.compile(r"\bonly\s+time\s+will\s+tell\b", re.I),
        ]

    def _scan_patterns(self, text: str, word_count: int) -> Dict[str, Any]:
        """Scans for hallmark phrases, templates, and hedging structures."""
        w = max(1, word_count)
        
        hallmark_matches: List[str] = []
        for pat in self._hallmark_phrases:
            found = pat.findall(text)
            if found:
                hallmark_matches.extend(found)

        boilerplate_matches: List[str] = []
        for pat in self._boilerplate_templates:
            found = pat.findall(text)
            if found:
                boilerplate_matches.extend(found)

        hedging_matches: List[str] = []
        for pat in self._hedging_patterns:
            found = pat.findall(text)
            if found:
                hedging_matches.extend(found)

        total_patterns = len(hallmark_matches) + len(boilerplate_matches) + len(hedging_matches)
        pattern_density = (total_patterns / w) * 100.0  # occurrences per 100 words

        return {
            "hallmark_count": len(hallmark_matches),
            "boilerplate_count": len(boilerplate_matches),
            "hedging_count": len(hedging_matches),
            "total_pattern_count": total_patterns,
            "pattern_density_per_100w": round(pattern_density, 3),
            "matched_hallmarks": list(set(hallmark_matches[:5])),
            "matched_templates": list(set(boilerplate_matches[:5]))
        }

    def analyze(self, doc: PreprocessedDocument) -> DetectorOutput:
        n_words = doc.total_words
        if n_words < 20:
            return DetectorOutput(
                module_name=self.name,
                display_name=self.display_name,
                raw_score=0.5,
                calibrated_score=0.5,
                confidence=0.1,
                observations=["Insufficient words to evaluate rhetorical pattern distributions."],
                features={"word_count": float(n_words)}
            )

        pattern_data = self._scan_patterns(doc.sanitized_text, n_words)
        density = pattern_data["pattern_density_per_100w"]

        features: Dict[str, float] = {
            "hallmark_count": float(pattern_data["hallmark_count"]),
            "boilerplate_count": float(pattern_data["boilerplate_count"]),
            "hedging_count": float(pattern_data["hedging_count"]),
            "total_pattern_count": float(pattern_data["total_pattern_count"]),
            "pattern_density_per_100w": density
        }

        # Scoring: Density per 100 words
        # 0 patterns in 300 words -> human (0.25)
        # 1-2 patterns -> neutral (0.50)
        # 3+ patterns -> AI bias (0.75+)
        # > 1.2 patterns per 100 words -> strong AI hallmark
        if density > 1.2:
            raw_score = 0.88
        elif density > 0.7:
            raw_score = 0.75
        elif density > 0.3:
            raw_score = 0.58
        elif pattern_data["total_pattern_count"] == 0 and n_words > 150:
            raw_score = 0.25
        else:
            raw_score = 0.45

        calibrated_score = 1.0 / (1.0 + math.exp(-4.2 * (raw_score - 0.50)))
        confidence = 0.4 if n_words < 60 else (0.75 if n_words < 200 else 0.90)

        observations: List[str] = []
        contradictions: List[str] = []

        if pattern_data["hallmark_count"] > 0:
            examples = ", ".join(f"'{m}'" for m in pattern_data["matched_hallmarks"])
            observations.append(
                f"Detected {pattern_data['hallmark_count']} model hallmark rhetorical markers: {examples}."
            )

        if pattern_data["boilerplate_count"] > 0:
            examples = ", ".join(f"'{m}'" for m in pattern_data["matched_templates"])
            observations.append(
                f"Identified formulaic boilerplate phrasing templates: {examples}."
            )

        if pattern_data["hedging_count"] > 0:
            observations.append(
                "Observed formulaic 'both sides' neutral counter-balancing templates."
            )

        # Passage scores
        passage_scores: List[PassageScore] = []
        for p in doc.passages:
            p_data = self._scan_patterns(p.text, p.word_count)
            p_dens = p_data["pattern_density_per_100w"]
            p_score = 0.78 if p_dens > 0.8 else (0.30 if p_data["total_pattern_count"] == 0 else 0.50)

            passage_scores.append(
                PassageScore(
                    passage_id=p.passage_id,
                    index=p.index,
                    score=round(p_score, 3),
                    confidence=round(confidence * 0.9, 3),
                    key_signals={"density": p_dens, "count": p_data["total_pattern_count"]},
                    summary=f"Patterns detected: {p_data['total_pattern_count']} (density {p_dens:.2f})"
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
            passage_scores=passage_scores,
            metadata={"matched_hallmarks": pattern_data["matched_hallmarks"]}
        )

