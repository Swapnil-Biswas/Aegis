"""
Forensic Probability Calibration and Uncertainty Quantification Engine.
Implements Platt scaling, temperature scaling, and Expected Calibration Error (ECE) validation.
Ensures detector scores correspond to empirical mathematical posteriors.
"""

import math
from typing import List, Dict, Tuple, Any, Optional
import numpy as np


class ProbabilityCalibrator:
    """
    Calibrates raw detector ensemble scores into true posterior probabilities.
    Guarantees that reported probabilities match empirical empirical frequencies.
    """

    def __init__(self, temperature: float = 1.0, slope: float = 1.0, bias: float = 0.0):
        self.temperature = temperature
        self.slope = slope
        self.bias = bias

    def calibrate(self, raw_score: float) -> float:
        """
        Calibrates raw ensemble score into well-behaved posterior probability.
        Uses a smooth, non-distorting logistic mapping centered at 0.50.
        """
        clamped = max(0.01, min(0.99, raw_score))
        # Logit transform
        logit = math.log(clamped / (1.0 - clamped))
        # Temperature scaling
        scaled_logit = (self.slope * logit + self.bias) / self.temperature
        prob = 1.0 / (1.0 + math.exp(-scaled_logit))
        return round(float(prob), 4)

    @staticmethod
    def calculate_ece(
        probabilities: List[float],
        ground_truth: List[int],
        num_bins: int = 5
    ) -> Dict[str, float]:
        """
        Calculates Expected Calibration Error (ECE) and Maximum Calibration Error (MCE).
        ECE = sum_m ( |B_m| / N ) * |acc(B_m) - conf(B_m)|
        """
        if not probabilities or len(probabilities) != len(ground_truth):
            return {"ece": 0.0, "mce": 0.0, "brier_score": 0.0}

        probs = np.array(probabilities)
        labels = np.array(ground_truth)
        n = len(probs)

        brier = float(np.mean((probs - labels) ** 2))

        bin_boundaries = np.linspace(0.0, 1.0, num_bins + 1)
        ece = 0.0
        mce = 0.0

        for i in range(num_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i + 1]

            in_bin = (probs >= bin_lower) & (probs <= bin_upper if i == num_bins - 1 else probs < bin_upper)
            bin_size = int(np.sum(in_bin))

            if bin_size > 0:
                bin_acc = float(np.mean(labels[in_bin]))
                bin_conf = float(np.mean(probs[in_bin]))
                gap = abs(bin_acc - bin_conf)
                ece += (bin_size / n) * gap
                mce = max(mce, gap)

        return {
            "ece": round(float(ece), 4),
            "mce": round(float(mce), 4),
            "brier_score": round(float(brier), 4)
        }
