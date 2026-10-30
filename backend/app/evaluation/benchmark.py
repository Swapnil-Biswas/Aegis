"""
AEGIS Scientific Benchmark and Validation Suite.
Executes systematic forensic evaluation across curated multi-model, multi-genre datasets.
Produces stratified slice evaluations and adversarial robustness profiles.
"""

import json
import os
from typing import List, Dict, Any, Optional

from app.core.preprocessor import ForensicPreprocessor
from app.detectors.statistical import StatisticalLinguisticDetector
from app.detectors.stylometric import StylometricFingerprintDetector
from app.detectors.neural import NeuralClassifierDetector
from app.detectors.semantic import SemanticDiscourseDetector
from app.detectors.pattern_analyzer import AIPatternDetector
from app.detectors.discontinuity import DiscontinuityDetector
from app.ensemble.fusion import ForensicEnsembleEngine, OperatingMode
from app.evaluation.metrics import EvaluationSuite
from app.evaluation.adversarial import AdversarialAttackSimulator
from app.config import config


class ForensicBenchmarkRunner:
    """
    Executes reproducible scientific validation across multi-domain datasets.
    """

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or os.path.join(
            os.path.dirname(__file__), "..", "data", "curated_benchmarks.json"
        )
        self.preprocessor = ForensicPreprocessor()
        
        # Initialize detector suite
        self.detectors = [
            StatisticalLinguisticDetector(),
            StylometricFingerprintDetector(),
            NeuralClassifierDetector(),
            SemanticDiscourseDetector(),
            AIPatternDetector(),
            DiscontinuityDetector()
        ]
        self.ensemble = ForensicEnsembleEngine()
        self.attacker = AdversarialAttackSimulator()

    def load_dataset(self) -> List[Dict[str, Any]]:
        """Loads curated evaluation benchmark samples."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Benchmark dataset not found at {self.data_path}")
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run_benchmark(self, mode: OperatingMode = OperatingMode.BALANCED) -> Dict[str, Any]:
        """
        Executes full benchmark evaluation across all dataset samples.
        Computes overall metrics, length slices, genre slices, and adversarial degradation.
        """
        dataset = self.load_dataset()
        y_true: List[int] = []
        y_probs: List[float] = []
        sample_results: List[Dict[str, Any]] = []

        # Stratification buckets
        genre_groups: Dict[str, Dict[str, List]] = {}
        length_groups: Dict[str, Dict[str, List]] = {
            "short (<100w)": {"y_true": [], "y_probs": []},
            "medium (100-250w)": {"y_true": [], "y_probs": []},
            "long (>250w)": {"y_true": [], "y_probs": []}
        }
        family_groups: Dict[str, Dict[str, List]] = {}

        for sample in dataset:
            text = sample["text"]
            is_ai = sample["is_ai"]
            genre = sample.get("genre", "general")
            family = sample.get("model_family", "unknown")

            doc = self.preprocessor.process(text)
            outputs = [d.analyze(doc) for d in self.detectors]
            decision = self.ensemble.fuse(doc, outputs, mode=mode)

            prob = decision.calibrated_ai_likelihood
            y_true.append(is_ai)
            y_probs.append(prob)

            # Store result metadata
            sample_results.append({
                "id": sample.get("id"),
                "genre": genre,
                "model_family": family,
                "word_count": doc.total_words,
                "ground_truth_is_ai": is_ai,
                "calibrated_ai_prob": prob,
                "verdict": decision.verdict.value,
                "confidence": decision.confidence
            })

            # Stratification by Genre
            if genre not in genre_groups:
                genre_groups[genre] = {"y_true": [], "y_probs": []}
            genre_groups[genre]["y_true"].append(is_ai)
            genre_groups[genre]["y_probs"].append(prob)

            # Stratification by Model Family
            if family not in family_groups:
                family_groups[family] = {"y_true": [], "y_probs": []}
            family_groups[family]["y_true"].append(is_ai)
            family_groups[family]["y_probs"].append(prob)

            # Stratification by Length
            if doc.total_words < 100:
                length_groups["short (<100w)"]["y_true"].append(is_ai)
                length_groups["short (<100w)"]["y_probs"].append(prob)
            elif doc.total_words <= 250:
                length_groups["medium (100-250w)"]["y_true"].append(is_ai)
                length_groups["medium (100-250w)"]["y_probs"].append(prob)
            else:
                length_groups["long (>250w)"]["y_true"].append(is_ai)
                length_groups["long (>250w)"]["y_probs"].append(prob)

        # 1. Overall Metrics
        overall_metrics = EvaluationSuite.compute_all_metrics(y_true, y_probs)

        # 2. Length Slice Metrics
        length_slice_metrics: Dict[str, Any] = {}
        for l_key, grp in length_groups.items():
            if len(grp["y_true"]) > 0:
                length_slice_metrics[l_key] = EvaluationSuite.compute_all_metrics(
                    grp["y_true"], grp["y_probs"]
                )

        # 3. Adversarial Robustness Stress Test on AI Samples
        adversarial_tests: List[Dict[str, Any]] = []
        ai_samples = [s for s in dataset if s["is_ai"] == 1][:3]
        total_drift = 0.0
        drift_count = 0

        for ai_s in ai_samples:
            clean_text = ai_s["text"]
            clean_doc = self.preprocessor.process(clean_text)
            clean_outputs = [d.analyze(clean_doc) for d in self.detectors]
            clean_decision = self.ensemble.fuse(clean_doc, clean_outputs, mode=mode)
            clean_score = clean_decision.calibrated_ai_likelihood

            attacks = self.attacker.generate_all_attacks(clean_text)
            for atk in attacks:
                atk_doc = self.preprocessor.process(atk.perturbed_text)
                atk_outputs = [d.analyze(atk_doc) for d in self.detectors]
                atk_decision = self.ensemble.fuse(atk_doc, atk_outputs, mode=mode)
                atk_score = atk_decision.calibrated_ai_likelihood

                drift = abs(clean_score - atk_score)
                total_drift += drift
                drift_count += 1

                adversarial_tests.append({
                    "sample_id": ai_s.get("id"),
                    "attack_type": atk.attack_type,
                    "clean_score": clean_score,
                    "perturbed_score": atk_score,
                    "score_drift": round(drift, 4),
                    "retained_detection": atk_score >= 0.50
                })

        avg_drift = round(total_drift / max(1, drift_count), 4)

        return {
            "evaluation_profile": mode.value,
            "overall_metrics": overall_metrics,
            "length_slice_metrics": length_slice_metrics,
            "adversarial_robustness": {
                "average_score_drift": avg_drift,
                "adversarial_tests": adversarial_tests
            },
            "sample_results": sample_results
        }


if __name__ == "__main__":
    runner = ForensicBenchmarkRunner()
    results = runner.run_benchmark()
    print("=== AEGIS SCIENTIFIC EVALUATION BENCHMARK RESULTS ===")
    print(f"Samples Evaluated: {results['overall_metrics']['sample_count']}")
    print(f"AUROC:             {results['overall_metrics']['auroc']}")
    print(f"AUPRC:             {results['overall_metrics']['auprc']}")
    print(f"F1-Score:          {results['overall_metrics']['f1_score']}")
    print(f"Precision:         {results['overall_metrics']['precision']}")
    print(f"Recall:            {results['overall_metrics']['recall']}")
    print(f"ECE (Calibration): {results['overall_metrics']['expected_calibration_error']}")
    print(f"Brier Score:       {results['overall_metrics']['brier_score']}")
    print(f"Adversarial Drift: {results['adversarial_robustness']['average_score_drift']}")

