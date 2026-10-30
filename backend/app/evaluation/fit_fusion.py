"""
Fits the AEGIS stacking fusion and reports held-out metrics.

  1. Downloads a labelled human / machine sample from public Hugging Face datasets
     (MAGE test split + RAID chat-model generations, no adversarial attacks).
  2. Runs every detector and records its document- and passage-level scores.
  3. Fits logistic-regression stackers on a stratified 50% development split for
     each module-availability tier (full / no classifier / heuristics only).
  4. Writes app/data/fusion_weights.json and app/data/evaluation_summary.json with
     metrics measured on the other 50%.

Usage (from backend/):  python -m app.evaluation.fit_fusion [--rows cached_rows.json]
"""

import argparse
import datetime
import json
import os
import random
import time
import urllib.request
from typing import Dict, List

import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ROWS_API = "https://datasets-server.huggingface.co/rows?dataset={ds}&config={cfg}&split={split}&offset={off}&length={n}"

MODULES = [
    "statistical_linguistics", "stylometric_fingerprinting", "neural_classifier",
    "lm_perplexity", "semantic_discourse", "pattern_analysis", "discontinuity_analysis",
]
TIERS = {
    "full": MODULES,
    "no_classifier": [m for m in MODULES if m != "neural_classifier"],
    "heuristic_only": [m for m in MODULES if m not in ("neural_classifier", "lm_perplexity")],
}


def _get(ds, cfg, split, off, n):
    url = ROWS_API.format(ds=ds, cfg=cfg, split=split, off=off, n=n)
    for attempt in range(8):
        try:
            rows = json.load(urllib.request.urlopen(url, timeout=90))["rows"]
            time.sleep(1.5)
            return rows
        except Exception:
            time.sleep(5 * (attempt + 1))
    return []


def fetch_corpus(seed: int = 11) -> List[Dict]:
    random.seed(seed)
    out = []
    for off in random.sample(range(0, 60600), 30):
        for r in _get("yaful/MAGE", "default", "test", off, 25):
            t = r["row"]["text"]
            if 60 <= len(t.split()) <= 700:
                human = int(r["row"]["label"]) == 1  # MAGE: 1 = human
                out.append({"is_ai": 0 if human else 1, "model": "human" if human else "machine",
                            "domain": r["row"]["src"], "text": t})
    for off in [12000, 12100, 20000, 20100, 1000500, 1500500]:
        for r in _get("liamdugan/raid", "raid", "train", off, 100):
            x = r["row"]
            if x["attack"] == "none" and x["model"] in ("mistral-chat", "llama-chat", "chatgpt", "gpt4", "cohere-chat") \
                    and len(x["generation"].split()) >= 60:
                out.append({"is_ai": 1, "model": x["model"], "domain": "raid_" + x["domain"], "text": x["generation"]})
    return out


def extract_rows(corpus: List[Dict]) -> List[Dict]:
    from app.core.preprocessor import ForensicPreprocessor
    from app.detectors.registry import get_detectors

    pre, dets, rows = ForensicPreprocessor(), get_detectors(), []
    for s in corpus:
        doc = pre.process(s["text"])
        outs = {o.module_name: o for o in (d.analyze(doc) for d in dets)}
        rows.append({
            "y": s["is_ai"], "model": s["model"], "domain": s["domain"], "words": doc.total_words,
            "scores": {k: o.calibrated_score for k, o in outs.items()},
        })
    return rows


def _logit(p):
    p = np.clip(np.asarray(p, dtype=float), 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def fit(rows: List[Dict]) -> None:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score, accuracy_score, brier_score_loss
    from sklearn.model_selection import train_test_split
    from app.core.calibrator import ProbabilityCalibrator

    y = np.array([r["y"] for r in rows])
    dev, test = train_test_split(np.arange(len(rows)), test_size=0.5, stratify=y, random_state=1)
    weights, metrics = {}, {}
    for tier, cols in TIERS.items():
        X = np.stack([_logit([r["scores"][m] for r in rows]) for m in cols], axis=1)
        lr = LogisticRegression(C=1.0).fit(X[dev], y[dev])
        p = lr.predict_proba(X[test])[:, 1]
        weights[tier] = {"intercept": round(float(lr.intercept_[0]), 4),
                         "coefficients": dict(zip(cols, [round(float(c), 4) for c in lr.coef_[0]]))}
        tn = int(((p < 0.5) & (y[test] == 0)).sum()); fp = int(((p >= 0.5) & (y[test] == 0)).sum())
        cal = ProbabilityCalibrator.calculate_ece(p.tolist(), y[test].tolist(), num_bins=10)
        metrics[tier] = {
            "auroc": round(float(roc_auc_score(y[test], p)), 4),
            "accuracy_at_0_5": round(float(accuracy_score(y[test], p >= 0.5)), 4),
            "false_positive_rate_at_0_5": round(fp / max(1, fp + tn), 4),
            "brier_score": round(float(brier_score_loss(y[test], p)), 4),
            "expected_calibration_error": cal["ece"],
        }
    single = {m: round(float(roc_auc_score(y[test], [rows[i]["scores"][m] for i in test])), 4) for m in MODULES}
    now = datetime.date.today().isoformat()
    with open(os.path.join(DATA_DIR, "fusion_weights.json"), "w") as f:
        json.dump({"fitted_on": now, "tiers": weights}, f, indent=2)
    summary = {
        "evaluated_on": now,
        "dataset": "Stratified 50% held-out split of a public sample: MAGE test split (yaful/MAGE) "
                   "+ RAID chat-model generations without attacks (liamdugan/raid).",
        "n_total": len(rows), "n_test": int(len(test)),
        "n_test_ai": int(y[test].sum()), "n_test_human": int(len(test) - y[test].sum()),
        "tiers": metrics, "single_module_auroc": single,
        "caveats": [
            "The default neural classifier's training data is not fully documented and may overlap "
            "with these public corpora; treat the 'full' tier numbers as optimistic.",
            "Adversarially paraphrased or heavily human-edited AI text was not part of this evaluation.",
            "English only.",
        ],
    }
    with open(os.path.join(DATA_DIR, "evaluation_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", help="Reuse cached extracted rows JSON instead of re-running detectors.")
    args = ap.parse_args()
    if args.rows and os.path.exists(args.rows):
        rows = json.load(open(args.rows))
    else:
        rows = extract_rows(fetch_corpus())
        if args.rows:
            json.dump(rows, open(args.rows, "w"))
    fit(rows)


if __name__ == "__main__":
    main()
