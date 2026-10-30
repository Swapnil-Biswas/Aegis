# AEGIS Forensic Validation & Benchmark Report

*Last measured: 2026-10-31. Reproduce with `cd backend && python -m app.evaluation.fit_fusion`.*

## 1. Datasets

| Set | Human | AI | Source |
| :--- | :--- | :--- | :--- |
| **Public mix** (fit + held-out test) | 458 | 338 | [MAGE](https://huggingface.co/datasets/yaful/MAGE) test split (human and machine text across many domains) + [RAID](https://huggingface.co/datasets/liamdugan/raid) generations from Mistral-chat and Llama-chat, no adversarial attacks |
| **Out-of-distribution** | 51 | 16 | Project Gutenberg paragraphs (human) + fresh passages written by a 2026 Claude model in 16 everyday registers (AI) |
| **Synthetic hybrids** | 30 docs | | One human and one AI paragraph concatenated, in both orders |

The fusion weights are fitted on a stratified 50% development split of the public mix. All numbers below come from the other 50% (398 texts: 169 AI, 229 human) or from the separate OOD and hybrid sets.

## 2. Held-out Results (public mix, balanced profile)

| Configuration | AUROC | Accuracy @0.5 | FPR @0.5 | Brier | ECE |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Full** (all modules) | **0.987** | **0.950** | **5.2%** | 0.036 | 0.048 |
| No classifier (perplexity + heuristics) | 0.900 | 0.857 | 8.3% | 0.117 | 0.117 |
| Heuristics only | 0.781 | 0.726 | 15.7% | 0.189 | 0.063 |
| *Previous release (random-init "neural" head + hand-tuned fusion)* | *0.735* | *0.627* | | | |

Single-module AUROC on the same split: neural classifier 0.988, LM perplexity 0.887, stylometry 0.724, statistical 0.722, patterns 0.611, discontinuity 0.516, semantic 0.514.

### Verdict distribution (all 796 public texts, balanced profile)

| Truth | HUMAN_AUTHENTIC | AI_GENERATED | INCONCLUSIVE |
| :--- | :--- | :--- | :--- |
| Human (458) | 416 (90.8%) | 6 (1.3%) | 36 (7.9%) |
| AI (338) | 16 (4.7%) | 316 (93.5%) | 6 (1.8%) |

The previous release returned `INCONCLUSIVE` for 794 of these 796 texts.

## 3. Out-of-distribution Check

- AUROC 0.974. No false positives on the 51 Gutenberg passages.
- Fresh Claude passages: 9/16 flagged `AI_GENERATED`, 2 `INCONCLUSIVE`, 5 missed. **Recall on the newest frontier models is noticeably lower than on the public benchmarks.**

## 4. Hybrid Documents

28 of 30 synthetic human+AI documents were labelled `HYBRID_MIXED`. In a control run of 30 pure-human and 30 pure-AI documents, none was labelled hybrid.

## 5. Caveats

- The default classifier (`fakespot-ai/roberta-base-ai-text-detection-v1`) does not fully document its training data, which may overlap with MAGE/RAID. Treat the "Full" numbers as optimistic. The OOD check gives a more conservative estimate.
- Adversarial paraphrasing, homoglyph attacks and heavy human post-editing were **not** evaluated. The `/stress-test` simulator measures score drift only, not detection accuracy under attack.
- English only. Short texts (<150 words) are less reliable, and texts under 60 words are refused.
- Detector output is probabilistic evidence, never proof of misconduct.
