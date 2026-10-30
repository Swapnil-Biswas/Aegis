"""
Module G: Adversarial Robustness and Attack Simulation Harness.
Simulates adversarial evasion tactics: synonym swaps, sentence restructuring,
contraction expansion/injection, human post-editing noise, and back-translation jitter.
Measures detector resilience and degradation curves quantitatively.
"""

import math
import random
import re
from typing import Dict, List, Any, Tuple
from pydantic import BaseModel, Field

from app.core.preprocessor import ForensicPreprocessor, PreprocessedDocument


class PerturbationResult(BaseModel):
    attack_type: str
    description: str
    perturbed_text: str
    perturbation_rate: float
    character_delta: int
    word_delta: int


class RobustnessEvaluationReport(BaseModel):
    original_score: float
    attack_results: List[Dict[str, Any]]
    mean_score_drift: float
    max_score_drift: float
    resilience_rating: str
    vulnerabilities_detected: List[str]


class AdversarialAttackSimulator:
    """
    Forensic stress-testing harness.
    Exposes detector sensitivity to intentional obfuscation attempts.
    """

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.preprocessor = ForensicPreprocessor()

        # Synonym substitution dictionary for common AI hallmarks & high-frequency words
        self._synonym_map = {
            "delve": "explore",
            "delves": "investigates",
            "testament": "proof",
            "tapestry": "mosaic",
            "foster": "encourage",
            "fosters": "promotes",
            "multifaceted": "complex",
            "pivotal": "central",
            "crucial": "vital",
            "furthermore": "also",
            "moreover": "in addition",
            "consequently": "as a result",
            "therefore": "so",
            "significant": "notable",
            "comprehensive": "thorough",
            "demonstrate": "show",
            "utilize": "use",
            "substantial": "large",
            "essential": "basic"
        }

        # Contraction mapping
        self._contraction_pairs = [
            ("do not", "don't"),
            ("cannot", "can't"),
            ("will not", "won't"),
            ("it is", "it's"),
            ("that is", "that's"),
            ("there is", "there's"),
            ("they are", "they're"),
            ("we are", "we're"),
            ("you are", "you're"),
            ("have not", "haven't")
        ]

    def attack_synonym_substitution(self, text: str, rate: float = 0.25) -> PerturbationResult:
        """Substitutes target words with everyday synonyms to evade lexical markers."""
        words = text.split()
        modified_words = []
        replaced_count = 0

        for w in words:
            clean_w = re.sub(r'[^\w]', '', w.lower())
            if clean_w in self._synonym_map and random.random() < rate:
                replacement = self._synonym_map[clean_w]
                # Preserve capitalization
                if w and w[0].isupper():
                    replacement = replacement.capitalize()
                # Preserve trailing punctuation
                trail = ""
                if w and not w[-1].isalnum():
                    trail = w[-1]
                modified_words.append(replacement + trail)
                replaced_count += 1
            else:
                modified_words.append(w)

        perturbed = " ".join(modified_words)
        return PerturbationResult(
            attack_type="synonym_substitution",
            description="Replaces hallmark vocabulary and formal transition words with informal synonyms.",
            perturbed_text=perturbed,
            perturbation_rate=round(replaced_count / max(1, len(words)), 3),
            character_delta=len(perturbed) - len(text),
            word_delta=len(modified_words) - len(words)
        )

    def attack_human_post_editing(self, text: str) -> PerturbationResult:
        """Simulates human post-editing by injecting contractions, em-dashes, and colloquial transitions."""
        perturbed = text
        changes = 0

        # Inject contractions
        for full, contracted in self._contraction_pairs:
            if re.search(r'\b' + full + r'\b', perturbed, re.IGNORECASE):
                perturbed = re.sub(r'\b' + full + r'\b', contracted, perturbed, count=2, flags=re.IGNORECASE)
                changes += 1

        # Inject occasional em-dash parenthetical
        sents = perturbed.split('. ')
        if len(sents) > 3:
            sents[1] = sents[1] + " — at least in most practical contexts —"
            changes += 1
            perturbed = '. '.join(sents)

        return PerturbationResult(
            attack_type="human_post_editing",
            description="Injects natural human contractions, parenthetical em-dashes, and stylistic pacing variance.",
            perturbed_text=perturbed,
            perturbation_rate=round(changes / max(1, len(text.split())), 3),
            character_delta=len(perturbed) - len(text),
            word_delta=len(perturbed.split()) - len(text.split())
        )

    def attack_sentence_inversion(self, text: str) -> PerturbationResult:
        """Inverts simple compound or coordinate clauses to break n-gram autoregressive sequence flow."""
        doc = self.preprocessor.process(text)
        new_sentences = []
        inverted_count = 0

        for s in doc.sentences:
            if ", but " in s.text and random.random() < 0.5:
                parts = s.text.split(", but ", 1)
                new_s = f"Although {parts[0].lower()}, {parts[1]}"
                new_sentences.append(new_s)
                inverted_count += 1
            elif ", although " in s.text:
                parts = s.text.split(", although ", 1)
                new_s = f"Although {parts[1].rstrip('.')}, {parts[0].lower()}."
                new_sentences.append(new_s)
                inverted_count += 1
            else:
                new_sentences.append(s.text)

        perturbed = " ".join(new_sentences)
        return PerturbationResult(
            attack_type="sentence_restructuring",
            description="Restructures subordinate and coordinate clauses to disrupt token predictability sequences.",
            perturbed_text=perturbed,
            perturbation_rate=round(inverted_count / max(1, len(doc.sentences)), 3),
            character_delta=len(perturbed) - len(text),
            word_delta=len(perturbed.split()) - len(text.split())
        )

    def attack_back_translation_simulation(self, text: str) -> PerturbationResult:
        """
        Simulates back-translation effects (e.g. English -> German -> English).
        Characterized by simplified syntax, slight word order shifts, and passive voice normalization.
        """
        words = text.split()
        substitutions = {
            "in conclusion": "finally",
            "in order to": "to",
            "a wide variety of": "various",
            "plays a pivotal role": "is very important",
            "it is evident that": "clearly",
            "furthermore": "moreover"
        }
        perturbed = text
        subs_applied = 0
        for phrase, rep in substitutions.items():
            if re.search(r'\b' + phrase + r'\b', perturbed, re.IGNORECASE):
                perturbed = re.sub(r'\b' + phrase + r'\b', rep, perturbed, flags=re.IGNORECASE)
                subs_applied += 1

        return PerturbationResult(
            attack_type="back_translation_simulation",
            description="Simulates automated round-trip translation syntax smoothing and idiomatic flattening.",
            perturbed_text=perturbed,
            perturbation_rate=round(subs_applied / max(1, len(words)), 3),
            character_delta=len(perturbed) - len(text),
            word_delta=len(perturbed.split()) - len(words)
        )

    def generate_all_attacks(self, text: str) -> List[PerturbationResult]:
        """Generates full suite of adversarial perturbations for robustness evaluation."""
        return [
            self.attack_synonym_substitution(text, rate=0.30),
            self.attack_human_post_editing(text),
            self.attack_sentence_inversion(text),
            self.attack_back_translation_simulation(text)
        ]

