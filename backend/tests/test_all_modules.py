"""
Comprehensive Automated Test Suite for AEGIS Forensic Detection System.
Validates all analytical modules, preprocessor invariants, non-negotiable rules,
and ensemble calibration.
"""

import unittest
import sys
import os

# Set path to include backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.preprocessor import ForensicPreprocessor
from app.detectors.statistical import StatisticalLinguisticDetector
from app.detectors.stylometric import StylometricFingerprintDetector
from app.detectors.neural import NeuralClassifierDetector
from app.detectors.semantic import SemanticDiscourseDetector
from app.detectors.pattern_analyzer import AIPatternDetector
from app.detectors.discontinuity import DiscontinuityDetector
from app.ensemble.fusion import ForensicEnsembleEngine, OperatingMode
from app.ensemble.thresholds import ClassificationVerdict
from app.core.calibrator import ProbabilityCalibrator
from app.evaluation.adversarial import AdversarialAttackSimulator


class TestForensicPreprocessor(unittest.TestCase):
    def setUp(self):
        self.preprocessor = ForensicPreprocessor(min_words_sufficient=60)

    def test_insufficient_evidence_rule(self):
        """Rule 7: Never silently classify insufficient evidence."""
        short_text = "This is a very short text sample."
        doc = self.preprocessor.process(short_text)
        self.assertFalse(doc.has_sufficient_evidence)
        self.assertIn("Scientific AI detection requires at least", doc.insufficiency_reason or "")

    def test_sentence_and_passage_boundaries(self):
        text = (
            "First sentence here. Second sentence follows immediately. "
            "Third sentence concludes the first thought. Fourth sentence begins a new perspective. "
            "Fifth sentence continues the argument. Sixth sentence finalizes the discussion."
        )
        doc = self.preprocessor.process(text)
        self.assertGreaterEqual(doc.total_sentences, 5)
        for s in doc.sentences:
            # Verify exact character slicing matches text
            self.assertEqual(text[s.start_char:s.end_char], s.text)


class TestModuleAStatistical(unittest.TestCase):
    def setUp(self):
        self.preprocessor = ForensicPreprocessor(min_words_sufficient=20)
        self.detector = StatisticalLinguisticDetector()

    def test_burstiness_and_entropy(self):
        text = (
            "We investigated mitochondrial dynamics in cultured murine cortical neurons. "
            "When cells were subjected to acute hypoxic stress, total ATP plummeted by 42%. "
            "However, exogenous NAD+ precursors rescued cristae junctions without restoring baseline respiration. "
            "These findings suggest mitochondrial elongation can operate through uncoupled pathways."
        )
        doc = self.preprocessor.process(text)
        out = self.detector.analyze(doc)
        self.assertIn("burstiness", out.features)
        self.assertIn("shannon_entropy", out.features)
        self.assertIn("hapax_ratio", out.features)
        self.assertGreater(out.features["shannon_entropy"], 2.0)


class TestModuleBStylometric(unittest.TestCase):
    def setUp(self):
        self.preprocessor = ForensicPreprocessor(min_words_sufficient=20)
        self.detector = StylometricFingerprintDetector()

    def test_stylometric_features(self):
        text = (
            "Furthermore, it is evident that the proposed framework functions effectively. "
            "Moreover, the system achieves remarkable stability under distributed network topologies. "
            "Consequently, developers can deploy applications without manual synchronization overhead."
        )
        doc = self.preprocessor.process(text)
        out = self.detector.analyze(doc)
        self.assertIn("formal_transition_ratio", out.features)
        self.assertIn("punctuation_entropy", out.features)
        self.assertIn("opening_uniqueness", out.features)
        self.assertGreater(out.features["formal_transition_ratio"], 0.0)


class TestModuleEPatterns(unittest.TestCase):
    def setUp(self):
        self.preprocessor = ForensicPreprocessor(min_words_sufficient=20)
        self.detector = AIPatternDetector()

    def test_ai_hallmark_detection(self):
        text = (
            "In today's fast-paced digital world, machine learning plays a crucial role. "
            "Delving into the algorithmic mechanisms, it is important to remember that technology fosters a vibrant "
            "tapestry of innovation, serving as a testament to human ingenuity. In conclusion, the benefits are vast."
        )
        doc = self.preprocessor.process(text)
        out = self.detector.analyze(doc)
        self.assertGreaterEqual(out.features["hallmark_count"], 2)
        self.assertGreaterEqual(out.features["boilerplate_count"], 1)
        self.assertGreater(out.calibrated_score, 0.60)


class TestModuleFDiscontinuity(unittest.TestCase):
    def setUp(self):
        self.preprocessor = ForensicPreprocessor(
            min_words_sufficient=40,
            passage_window_words=50,
            passage_stride_words=25
        )
        self.detector = DiscontinuityDetector()

    def test_composite_hybrid_divergence(self):
        # Mixture of conversational slang and formal academic prose across multiple passages
        text = (
            "Yo what's up guys, today we are checking out this super cool mechanical keyboard! "
            "I literally cannot believe how fast the switches actuate when I'm gaming. Totally wild experience! "
            "The RGB backlighting is super bright and the keycaps feel completely premium in your hands. "
            "Definitely smash that like button and subscribe for more daily tech reviews and setup guides! "
            "The mitochondrial outer membrane permeabilization represents an irreversible commitment step to apoptosis. "
            "Bcl-2 family proteins strictly regulate the oligomerization of Bak and Bax at the outer mitochondrial surface. "
            "Cytochrome c release triggers the downstream formation of the apoptosome complex with Apaf-1 and procaspase-9."
        )
        doc = self.preprocessor.process(text)
        self.assertGreaterEqual(len(doc.passages), 2)
        out = self.detector.analyze(doc)
        self.assertIn("discontinuity_index", out.features)
        self.assertGreater(out.features["discontinuity_index"], 0.10)


class TestNonNegotiableRulesAndEnsemble(unittest.TestCase):
    def setUp(self):
        self.preprocessor = ForensicPreprocessor(min_words_sufficient=60)
        self.ensemble = ForensicEnsembleEngine()
        self.detectors = [
            StatisticalLinguisticDetector(),
            StylometricFingerprintDetector(),
            NeuralClassifierDetector(),
            SemanticDiscourseDetector(),
            AIPatternDetector(),
            DiscontinuityDetector()
        ]

    def test_rule_1_never_100_percent_certainty(self):
        """Rule 1: Never claim 100% detection accuracy."""
        ai_text = (
            "In today's fast-paced digital landscape, artificial intelligence plays a crucial role in transforming "
            "traditional educational methodologies. It is important to remember that technology does not merely "
            "replace the instructor; rather, it fosters a vibrant and multifaceted learning environment tailored to "
            "diverse student needs. Delving into the pedagogical implications, one observes a profound synergy "
            "between machine learning algorithms and personalized curriculum delivery. Furthermore, modern adaptive "
            "platforms provide nuanced insights into cognitive retention. Ultimately, the integration of these "
            "sophisticated systems stands as a testament to the ever-evolving nature of global education."
        )
        doc = self.preprocessor.process(ai_text)
        outputs = [d.analyze(doc) for d in self.detectors]
        decision = self.ensemble.fuse(doc, outputs, mode=OperatingMode.BALANCED)
        # Check that likelihood is strictly less than 1.0 and confidence is strictly less than 1.0
        self.assertLess(decision.calibrated_ai_likelihood, 1.0)
        self.assertLess(decision.confidence, 1.0)

    def test_rule_7_insufficient_evidence_verdict(self):
        """Rule 7: Never silently classify insufficient evidence."""
        short_text = "This short snippet cannot be evaluated."
        doc = self.preprocessor.process(short_text)
        outputs = [d.analyze(doc) for d in self.detectors]
        decision = self.ensemble.fuse(doc, outputs, mode=OperatingMode.BALANCED)
        self.assertEqual(decision.verdict, ClassificationVerdict.INSUFFICIENT_EVIDENCE)


class TestAdversarialSimulator(unittest.TestCase):
    def setUp(self):
        self.attacker = AdversarialAttackSimulator()

    def test_perturbation_generation(self):
        text = "Furthermore, delving into this multifaceted topic is crucial because it serves as a testament to progress."
        results = self.attacker.generate_all_attacks(text)
        self.assertEqual(len(results), 4)
        for r in results:
            self.assertIsNotNone(r.perturbed_text)
            self.assertNotEqual(r.perturbed_text, "")


if __name__ == "__main__":
    unittest.main()
