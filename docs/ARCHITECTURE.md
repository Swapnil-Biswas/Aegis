# AEGIS System Architecture Specification

## 1. System Topology Overview

AEGIS (Advanced Empirical Generation Identification & Stylometry) is designed as a decomposed, multi-layer forensic intelligence system. Rather than relying on a single neural head or an uncalibrated heuristic, the architecture enforces independent module execution, evidence calibration, and explicit uncertainty quantification.

```
+-------------------------------------------------------------------------+
|                           Client Application                            |
|             (React 18 / TypeScript / Tailwind CSS Dashboard)             |
+------------------------------------+------------------------------------+
                                     | HTTP / JSON / Multipart
                                     v
+------------------------------------+------------------------------------+
|                         FastAPI Core Engine                             |
|  - Rate Limiting & Input Sanitization                                   |
|  - File Parser (TXT / PDF via pypdf / DOCX via python-docx)             |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                   Forensic Preprocessor & Boundary Slicer               |
|  - Zero-width character & malicious unicode stripping                   |
|  - Strict sentence boundary mapping (exact character offsets)           |
|  - Minimum Evidence Rule Check (60 words threshold)                     |
|  - Semantic sliding-window passage chunker (120w window, 50w stride)   |
+------------------------------------+------------------------------------+
                                     |
    +--------------------------------+--------------------------------+
    |                                                                 |
    v                                                                 v
+---+----------------------------------+   +--------------------------+---+
| Layer A: Statistical Linguistics     |   | Layer B: Stylometric Engine  |
| - Pseudo-Perplexity & Burstiness     |   | - Syntactic Complexity       |
| - Shannon Entropy of Tokens          |   | - Punctuation Entropy        |
| - Lexical Diversity (TTR, Hapax, K)  |   | - Function Word Vector       |
| - Zipfian Power-Law Fit (alpha, R^2) |   | - Contractions & Active/Pass |
+---+----------------------------------+   +--------------------------+---+
    |                                                                 |
    v                                                                 v
+---+----------------------------------+   +--------------------------+---+
| Layer C: Neural Detection Engine     |   | Layer D: Semantic Discourse  |
| - Transformer Sequence Embeddings    |   | - Consecutive Sentence Cosine|
| - Multi-Layer Perceptron Projection  |   | - Semantic Smoothness Index  |
| - Calibrated Logits & Margin Conf    |   | - Redundant Conclusion Check |
+---+----------------------------------+   +--------------------------+---+
    |                                                                 |
    v                                                                 v
+---+----------------------------------+   +--------------------------+---+
| Layer E: AI Generation Patterns      |   | Layer F: Discontinuity/Hybrid|
| - Hallmark N-Grams ("testament to")  |   | - Inter-passage JSD Divergence|
| - Rhetorical Boilerplate Templates   |   | - Authorial Boundary Shifts  |
| - Neutral "Both Sides" Hedging       |   | - Human/AI Composite Slicing |
+---+----------------------------------+   +--------------------------+---+
    |                                                                 |
    +--------------------------------+--------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                 Calibrated Ensemble & Decision Core                     |
|  - Reliability-Weighted Bayesian Stacking                               |
|  - Platt & Temperature Scaling (ECE < 0.10)                             |
|  - Operating Profiles (High-Precision, Balanced, Exploratory)           |
|  - Inter-Module Variance & Contradiction Isolation                      |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                     Forensic Explanation Engine                         |
|  - Fact vs Model Prediction vs Statistical Correlation Separation       |
|  - Passage-level Heatmap Attribution (Green / Yellow / Red / Gray)      |
|  - Structured Forensic Audit Report (JSON / Markdown / Printable)       |
+-------------------------------------------------------------------------+
```

## 2. Sliding-Window Semantic Passage Algorithm

To avoid document-level aggregation bias and accurately detect hybrid/mixed human-AI compositions:
1. Sentence tokens $S = \{s_1, s_2, \dots, s_n\}$ are extracted with character indices $[c_{\text{start}}, c_{\text{end}}]$.
2. A sliding window of $W = 120$ words steps across sentence boundaries with a stride of $S_{\text{stride}} = 50$ words.
3. Sentence boundaries are never fractured mid-sentence, preserving grammatical integrity.
4. Each passage is independently analyzed by all six analytical layers, generating localized likelihood and confidence scores.
5. Adjacent passage character n-gram Jensen-Shannon Divergence ($D_{\text{JS}}$) is calculated to localize exact composite boundaries.

## 3. The 3 Operational Threshold Profiles

Forensic investigations require different risk appetites:
- **High-Precision Mode (AI Threshold $\ge 0.82$, Human Threshold $\le 0.20$):**
  Engineered for academic misconduct investigations or formal evidentiary proceedings. Guarantees False Positive Rate $< 1\%$.
- **Balanced Mode (AI Threshold $\ge 0.65$, Human Threshold $\le 0.35$):**
  Optimized for editorial workflows, publishing houses, and general content auditing.
- **Exploratory Mode (AI Threshold $\ge 0.50$, Human Threshold $\le 0.50$):**
  High sensitivity screening to flag candidate text for human forensic review.

