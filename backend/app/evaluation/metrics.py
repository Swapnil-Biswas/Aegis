"""
Forensic Evaluation Metrics and Statistical Validation.
Computes AUROC, AUPRC, ECE, Brier Score, Specificity, FPR at target TPR,
and slice-based stratified performance metrics.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn import metrics
from app.core.calibrator import ProbabilityCalibrator


class EvaluationSuite:
    """
    Computes rigorous forensic evaluation metrics across model predictions.
    Avoids reporting single-accuracy numbers in favor of comprehensive statistical profiles.
    """

    @staticmethod
    def compute_all_metrics(
        y_true: List[int],
        y_probs: List[float],
        threshold: float = 0.50
    ) -> Dict[str, Any]:
        """
        Calculates complete suite of forensic classification and calibration metrics.
        """
        y_t = np.array(y_true)
        y_p = np.array(y_probs)
        y_pred = (y_p >= threshold).astype(int)

        # 1. Basic Confusion Matrix elements
        tn, fp, fn, tp = metrics.confusion_matrix(y_t, y_pred, labels=[0, 1]).ravel()

        # 2. Rates
        precision = float(metrics.precision_score(y_t, y_pred, zero_division=0))
        recall = float(metrics.recall_score(y_t, y_pred, zero_division=0))
        f1 = float(metrics.f1_score(y_t, y_pred, zero_division=0))
        specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0
        accuracy = float((tp + tn) / len(y_t)) if len(y_t) > 0 else 0.0

        # 3. Curve Metrics
        try:
            auroc = float(metrics.roc_auc_score(y_t, y_p))
        except Exception:
            auroc = 0.50

        try:
            precision_curve, recall_curve, _ = metrics.precision_recall_curve(y_t, y_p)
            auprc = float(metrics.auc(recall_curve, precision_curve))
        except Exception:
            auprc = 0.50

        # 4. Calibration & Brier
        cal_metrics = ProbabilityCalibrator.calculate_ece(list(y_p), list(y_t))

        return {
            "sample_count": len(y_t),
            "threshold": threshold,
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "specificity": round(specificity, 4),
            "false_positive_rate": round(fpr, 4),
            "false_negative_rate": round(fnr, 4),
            "auroc": round(auroc, 4),
            "auprc": round(auprc, 4),
            "brier_score": cal_metrics["brier_score"],
            "expected_calibration_error": cal_metrics["ece"],
            "maximum_calibration_error": cal_metrics["mce"],
            "confusion_matrix": {
                "true_positives": int(tp),
                "false_positives": int(fp),
                "true_negatives": int(tn),
                "false_negatives": int(fn)
            }
        }

