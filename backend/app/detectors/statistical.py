"""
Module A: Statistical Linguistic Analysis.
Computes token distributions, perplexity proxies, burstiness, Shannon entropy,
lexical diversity (TTR, Hapax, Yule's K), Zipfian divergence, and N-gram repetition.
"""

import math
import re
from collections import Counter
from typing import Dict, List, Any, Tuple
import numpy as np
from scipy import stats

from app.core.preprocessor import PreprocessedDocument, PassageChunk, TextSpan
from app.detectors.base import BaseDetector, DetectorOutput, PassageScore


class StatisticalLinguisticDetector(BaseDetector):
    """
    Forensic statistical linguistics engine.
    Analyzes mathematical properties of text distributions without relying
    on a single heuristic or equating polished writing with AI.
    """

    def __init__(self, weight: float = 1.0):
        super().__init__(
            name="statistical_linguistics",
            display_name="Statistical Linguistic Analysis",
            weight=weight
        )
        # Standard unigram frequency reference model derived from balanced human corpora (Brown/BNC)
        # Used for relative entropy and Zipfian divergence comparison
        self._common_english_words = {
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her",
            "she", "or", "an", "will", "my", "one", "all", "would", "there",
            "their", "what", "so", "up", "out", "if", "about", "who", "get",
            "which", "go", "me", "when", "make", "can", "like", "time", "no",
            "just", "him", "know", "take", "people", "into", "year", "your",
            "good", "some", "could", "them", "see", "other", "than", "then",
            "now", "look", "only", "come", "its", "over", "think", "also"
        }

    def _tokenize_words(self, text: str) -> List[str]:
        """Low-level word tokenization ignoring punctuation."""
        return re.findall(r'\b[a-zA-Z0-9_\'-]+\b', text.lower())

    def _compute_shannon_entropy(self, tokens: List[str]) -> float:
        """Calculates Shannon entropy in bits for token frequencies."""
        if not tokens:
            return 0.0
        counts = Counter(tokens)
        total = len(tokens)
        entropy = 0.0
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)
        return float(entropy)

    def _compute_lexical_diversity(self, tokens: List[str]) -> Dict[str, float]:
        """
        Computes robust lexical diversity indicators:
        - TTR (Type-Token Ratio)
        - Root TTR (RTTR = V / sqrt(2N))
        - Hapax Legomena Ratio (V_1 / N)
        - Dislegomena Ratio (V_2 / N)
        - Yule's Characteristic K
        """
        N = len(tokens)
        if N == 0:
            return {
                "ttr": 0.0,
                "root_ttr": 0.0,
                "hapax_ratio": 0.0,
                "dislegomena_ratio": 0.0,
                "yules_k": 0.0
            }

        counts = Counter(tokens)
        V = len(counts)
        freq_spectrum = Counter(counts.values())

        # Hapax legomena: words appearing exactly once
        V1 = freq_spectrum.get(1, 0)
        # Dislegomena: words appearing exactly twice
        V2 = freq_spectrum.get(2, 0)

        ttr = V / N
        root_ttr = V / math.sqrt(2 * N) if N > 0 else 0.0
        hapax_ratio = V1 / N
        dislegomena_ratio = V2 / N

        # Yule's K: K = 10^4 * (sum(m^2 * V_m) - N) / N^2
        # Invariant to text length for sufficiently large samples
        sum_m2_vm = sum((m ** 2) * vm for m, vm in freq_spectrum.items())
        yules_k = 10000.0 * (sum_m2_vm - N) / (N ** 2) if N > 1 else 0.0

        return {
            "ttr": round(float(ttr), 4),
            "root_ttr": round(float(root_ttr), 4),
            "hapax_ratio": round(float(hapax_ratio), 4),
            "dislegomena_ratio": round(float(dislegomena_ratio), 4),
            "yules_k": round(float(yules_k), 4)
        }

    def _compute_zipf_divergence(self, tokens: List[str]) -> Dict[str, float]:
        """
        Computes Zipf's Law rank-frequency fit.
        Natural human text strictly adheres to power-law alpha ~ 1.0.
        AI generation frequently shows compressed rank variance in the top 200 words.
        """
        if len(tokens) < 30:
            return {"zipf_alpha": 1.0, "zipf_r2": 1.0}

        counts = Counter(tokens)
        frequencies = sorted(counts.values(), reverse=True)
        ranks = np.arange(1, len(frequencies) + 1)

        # Log-log linear regression: log(freq) = -alpha * log(rank) + c
        log_ranks = np.log(ranks)
        log_freqs = np.log(frequencies)

        if len(log_ranks) > 2:
            slope, intercept, r_value, _, _ = stats.linregress(log_ranks, log_freqs)
            alpha = -slope
            r2 = r_value ** 2
        else:
            alpha = 1.0
            r2 = 1.0

        return {
            "zipf_alpha": round(float(alpha), 4),
            "zipf_r2": round(float(r2), 4)
        }

    def _compute_sentence_length_burstiness(self, sentences: List[TextSpan]) -> Dict[str, float]:
        """
        Measures variance and burstiness of sentence lengths.
        Burstiness B = sigma / mu (coefficient of variation).
        Human writing typically has B > 0.45; AI generation often has B in [0.20, 0.38].
        """
        if not sentences:
            return {
                "mean_sentence_length": 0.0,
                "std_sentence_length": 0.0,
                "burstiness": 0.0,
                "kurtosis": 0.0
            }

        lengths = [s.word_count for s in sentences if s.word_count > 0]
        if not lengths:
            return {
                "mean_sentence_length": 0.0,
                "std_sentence_length": 0.0,
                "burstiness": 0.0,
                "kurtosis": 0.0
            }

        mean_len = float(np.mean(lengths))
        std_len = float(np.std(lengths))
        burstiness = (std_len / mean_len) if mean_len > 0 else 0.0
        kurt = float(stats.kurtosis(lengths)) if len(lengths) > 4 else 0.0

        return {
            "mean_sentence_length": round(mean_len, 2),
            "std_sentence_length": round(std_len, 2),
            "burstiness": round(burstiness, 4),
            "kurtosis": round(kurt, 4)
        }

    def _compute_ngram_repetition(self, tokens: List[str]) -> Dict[str, float]:
        """
        Computes 2-gram and 3-gram repetition indexes.
        Excessive repetitive n-grams indicate autoregressive loops or template usage.
        """
        if len(tokens) < 4:
            return {"bigram_repetition": 0.0, "trigram_repetition": 0.0}

        bigrams = [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens) - 1)]
        trigrams = [f"{tokens[i]}_{tokens[i+1]}_{tokens[i+2]}" for i in range(len(tokens) - 2)]

        bi_rep = 1.0 - (len(set(bigrams)) / len(bigrams)) if bigrams else 0.0
        tri_rep = 1.0 - (len(set(trigrams)) / len(trigrams)) if trigrams else 0.0

        return {
            "bigram_repetition": round(float(bi_rep), 4),
            "trigram_repetition": round(float(tri_rep), 4)
        }

    def _estimate_pseudo_perplexity(self, tokens: List[str]) -> float:
        """
        Statistical pseudo-perplexity proxy based on rank frequency penalization.
        Lower values indicate standard predictable sequences; high values indicate unexpected vocabulary.
        """
        if not tokens:
            return 50.0

        # Measure log-likelihood against empirical frequency distribution
        counts = Counter(tokens)
        total = len(tokens)
        log_prob_sum = 0.0

        for t in tokens:
            # Common English word baseline
            base_p = 0.05 if t in self._common_english_words else 0.001
            empirical_p = counts[t] / total
            p = 0.7 * empirical_p + 0.3 * base_p
            log_prob_sum += math.log(max(p, 1e-6))

        pseudo_ppl = math.exp(-log_prob_sum / total)
        return round(float(pseudo_ppl), 2)

    def analyze(self, doc: PreprocessedDocument) -> DetectorOutput:
        tokens = self._tokenize_words(doc.sanitized_text)
        n_tokens = len(tokens)

        if n_tokens < 10:
            return DetectorOutput(
                module_name=self.name,
                display_name=self.display_name,
                raw_score=0.5,
                calibrated_score=0.5,
                confidence=0.1,
                observations=["Insufficient tokens to compute meaningful statistical linguistic metrics."],
                features={"word_count": float(n_tokens)}
            )

        # 1. Feature extractions
        entropy = self._compute_shannon_entropy(tokens)
        lexical = self._compute_lexical_diversity(tokens)
        zipf = self._compute_zipf_divergence(tokens)
        burst_info = self._compute_sentence_length_burstiness(doc.sentences)
        ngrams = self._compute_ngram_repetition(tokens)
        ppl = self._estimate_pseudo_perplexity(tokens)

        features: Dict[str, float] = {
            "token_count": float(n_tokens),
            "shannon_entropy": round(entropy, 4),
            "pseudo_perplexity": ppl,
            **lexical,
            **zipf,
            **burst_info,
            **ngrams
        }

        # 2. Multi-feature calibrated likelihood estimation
        # Human signals:
        # - High burstiness (B > 0.45)
        # - High Hapax legomena ratio (> 0.40)
        # - Higher Shannon entropy relative to text length
        # - Natural Zipfian alpha around 0.85 - 1.15
        #
        # AI signals:
        # - Low burstiness (B < 0.35, uniform sentence lengths)
        # - Compressed Hapax ratio (fewer unique rare words)
        # - High pseudo-perplexity predictability
        # - Higher n-gram repetition

        ai_indicators = 0.0
        weights_sum = 0.0

        # Burstiness component (weight: 2.0)
        b = burst_info["burstiness"]
        if b < 0.28:
            ai_indicators += 2.0 * 0.85
        elif b < 0.38:
            ai_indicators += 2.0 * 0.65
        elif b > 0.50:
            ai_indicators += 2.0 * 0.20
        else:
            ai_indicators += 2.0 * 0.45
        weights_sum += 2.0

        # Hapax legomena component (weight: 1.5)
        # Note: Raw hapax ratio is naturally inflated in short texts (N < 150).
        # Adjust threshold based on token count to prevent false human attribution on short AI samples.
        hapax = lexical["hapax_ratio"]
        expected_short_hapax = 0.65 if n_tokens < 150 else 0.40
        if hapax < expected_short_hapax - 0.15:
            ai_indicators += 1.5 * 0.80
        elif hapax < expected_short_hapax:
            ai_indicators += 1.5 * 0.65
        elif hapax > expected_short_hapax + 0.15 and n_tokens >= 150:
            ai_indicators += 1.5 * 0.20
        else:
            ai_indicators += 1.5 * 0.50
        weights_sum += 1.5

        # Yule's K component (weight: 1.0)
        # Higher Yule's K indicates higher vocabulary concentration (repetition)
        yk = lexical["yules_k"]
        if yk > 180:
            ai_indicators += 1.0 * 0.70
        elif yk < 100:
            ai_indicators += 1.0 * 0.35
        else:
            ai_indicators += 1.0 * 0.50
        weights_sum += 1.0

        # Zipf's Law R^2 component (weight: 1.0)
        # Synthetic text often displays artificially high or skewed R^2
        if zipf["zipf_alpha"] > 1.25 or zipf["zipf_alpha"] < 0.70:
            ai_indicators += 1.0 * 0.65
        else:
            ai_indicators += 1.0 * 0.35
        weights_sum += 1.0

        # N-gram repetition (weight: 1.0)
        if ngrams["bigram_repetition"] > 0.12:
            ai_indicators += 1.0 * 0.75
        elif ngrams["bigram_repetition"] < 0.05:
            ai_indicators += 1.0 * 0.30
        else:
            ai_indicators += 1.0 * 0.50
        weights_sum += 1.0

        raw_score = ai_indicators / weights_sum
        # Calibrated score using temperature scaling sigmoid
        calibrated_score = 1.0 / (1.0 + math.exp(-4.0 * (raw_score - 0.50)))

        # Confidence depends on text length (short text has wide confidence bounds)
        if n_tokens < 60:
            confidence = 0.25
        elif n_tokens < 150:
            confidence = 0.55
        elif n_tokens < 300:
            confidence = 0.75
        else:
            confidence = 0.90

        # 3. Observations and Contradictions
        observations: List[str] = []
        contradictions: List[str] = []

        if burst_info["burstiness"] < 0.30:
            observations.append(
                f"Sentence length burstiness is unusually low (B={burst_info['burstiness']}), "
                "indicating unnatural cadence uniformity across sentences."
            )
        elif burst_info["burstiness"] > 0.50:
            observations.append(
                f"Sentence length burstiness is robust (B={burst_info['burstiness']}), "
                "consistent with natural human stylistic pacing variance."
            )

        if lexical["hapax_ratio"] < 0.28:
            observations.append(
                f"Hapax legomena ratio is low ({lexical['hapax_ratio']:.1%}), showing constrained rare vocabulary deployment."
            )
        elif lexical["hapax_ratio"] > 0.42:
            observations.append(
                f"High hapax legomena frequency ({lexical['hapax_ratio']:.1%}) indicates rich idiosyncratic lexical choice."
            )

        # Check for contradictions
        if burst_info["burstiness"] > 0.55 and calibrated_score > 0.65:
            contradictions.append(
                "High sentence burstiness conflicts with other repetitive statistical signals; "
                "sample may be human writing with formulaic phrasing or human-edited AI text."
            )
        if lexical["hapax_ratio"] > 0.45 and calibrated_score > 0.60:
            contradictions.append(
                "High lexical richness contradicts low entropy indicators; topic-specific jargon may be elevating diversity."
            )

        # 4. Passage-level scoring
        passage_scores: List[PassageScore] = []
        for p in doc.passages:
            p_tokens = self._tokenize_words(p.text)
            if len(p_tokens) >= 15:
                p_burst = self._compute_sentence_length_burstiness([
                    doc.sentences[idx] for idx in p.sentence_indices if idx < len(doc.sentences)
                ])
                p_lex = self._compute_lexical_diversity(p_tokens)
                p_score = 0.5
                if p_burst["burstiness"] < 0.32 and p_lex["hapax_ratio"] < 0.32:
                    p_score = 0.78
                elif p_burst["burstiness"] > 0.48 and p_lex["hapax_ratio"] > 0.40:
                    p_score = 0.22
                else:
                    p_score = 0.50

                passage_scores.append(
                    PassageScore(
                        passage_id=p.passage_id,
                        index=p.index,
                        score=round(p_score, 3),
                        confidence=round(min(confidence, len(p_tokens) / 100.0), 3),
                        key_signals={
                            "burstiness": p_burst["burstiness"],
                            "hapax_ratio": p_lex["hapax_ratio"]
                        },
                        summary=f"Passage B={p_burst['burstiness']:.2f}, Hapax={p_lex['hapax_ratio']:.2f}"
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
