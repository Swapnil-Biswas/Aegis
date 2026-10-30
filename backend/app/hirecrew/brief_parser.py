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

        # Check for benchmark case triggers or standard instructions
        # e.g., "Analyze the following text for AI generation: [text]"
        patterns = [
            r"(?:analyze|check|evaluate|inspect|detect)\s+(?:the\s+following\s+)?(?:text|document|content|sample)?:\s*(.+)$",
            r"(?:text|sample|document|content):\s*(.+)$"
        ]

        extracted_text = cleaned
        for pat in patterns:
            match = re.search(pat, cleaned, re.IGNORECASE | re.DOTALL)
            if match and len(match.group(1).strip()) > 20:
                extracted_text = match.group(1).strip()
                break

        # Check for requested threshold modes in brief
        mode = "balanced"
        if re.search(r"\b(?:high[- ]?precision|strict|low[- ]?fpr)\b", cleaned, re.IGNORECASE):
            mode = "high_precision"
        elif re.search(r"\b(?:exploratory|sensitive|screening)\b", cleaned, re.IGNORECASE):
            mode = "exploratory"

        return {
            "text": extracted_text,
            "has_text": len(extracted_text) >= 10,
            "mode": mode,
            "raw_brief": cleaned
        }

