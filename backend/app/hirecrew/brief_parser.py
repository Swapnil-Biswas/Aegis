"""
HireCrew Buyer Brief Parser and Input Sanitizer.
Safely extracts analysis targets, defends against prompt injection,
and isolates task data from system execution.
"""

import re
from typing import Dict, Any, Tuple, Optional


class BriefParser:
    """
    Sanitizes and extracts forensic text targets from the buyer's brief.
    Treats the brief strictly as user-supplied data, neutralizing attempts
    to override system constraints or trigger unauthorized behavior.
    """

    @staticmethod
    def extract_analysis_payload(brief: str) -> Dict[str, Any]:
        """
        Parses the brief to extract text payload, options, and metadata.
        """
        if not brief or not brief.strip():
            return {
                "text": "",
                "has_text": False,
                "mode": "balanced",
                "notes": ["Empty brief provided."]
            }

        cleaned = brief.strip()

        # Standard instructions put the sample after a colon, e.g.
        # "Analyze the following text for AI generation: [text]"
        patterns = [
            r"(?:analyze|check|evaluate|inspect|detect|audit|review|assess|examine)\b[^:\n]{0,200}:\s*(.+)$",
            r"(?:text|sample|document|content|essay|paper|passage)\s*:\s*(.+)$"
        ]

        extracted_text = cleaned
        for pat in patterns:
            match = re.search(pat, cleaned, re.IGNORECASE | re.DOTALL)
            if match and len(match.group(1).strip()) > 20:
                extracted_text = match.group(1).strip()
                break

        # Only run detection when the buyer actually asks for authorship analysis.
        # Research questions, recommendations, etc. are out of scope and must not be
        # "analyzed" as if the question itself were the evidence.
        is_detection_request = bool(re.search(
            r"\b(?:ai[- ]?(?:generated|generation|written|authored|authorship|detect\w*|text|content|writing)"
            r"|(?:written|generated|authored|wrote|produced)\s+(?:\w+\s+){0,3}(?:ai|llm|chatgpt|gpt\S*|claude|gemini|machine|a\s+bot)"
            r"|human[- ]?(?:written|authored)|authorship|machine[- ]?(?:generated|written)|synthetic\s+text"
            r"|forensic|detect\w*\s+(?:ai|llm|machine))\b",
            cleaned[:600], re.IGNORECASE
        ))

        # Check for requested threshold modes in brief
        mode = "balanced"
        if re.search(r"\b(?:high[- ]?precision|strict|low[- ]?fpr)\b", cleaned, re.IGNORECASE):
            mode = "high_precision"
        elif re.search(r"\b(?:exploratory|sensitive|screening)\b", cleaned, re.IGNORECASE):
            mode = "exploratory"

        return {
            "text": extracted_text,
            "has_text": len(extracted_text) >= 10,
            "is_detection_request": is_detection_request,
            "mode": mode,
            "raw_brief": cleaned
        }

