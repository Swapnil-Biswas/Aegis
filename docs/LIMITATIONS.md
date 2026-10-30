# AEGIS Epistemic Limitations & Responsible Use Policy

## 1. The Fundamental Epistemic Boundary

No AI text detection system can achieve 100% mathematical certainty. Large language models and human authors draw from the same English vocabulary and share foundational syntactic constraints. 

AEGIS provides calibrated probabilistic evidence based on computed linguistic metrics; it does **not** provide definitive proof of author identity or moral integrity.

---

## 2. Documented Edge Cases and Failure Modes

### 1. Second-Language (ESL) Authors
Authors writing in English as an additional language frequently rely on standard textbook transitional templates (e.g. *"In conclusion"*, *"Furthermore"*, *"It is important to remember"*). In short texts, this can artificially elevate stylometric transition scores. AEGIS addresses this by checking sentence burstiness and lexical entropy, but human review is strictly required.

### 2. Standardized & Formulaic Genres
Legal contracts, software API specifications, laboratory chemical protocols, and insurance policies are deliberately designed with repetitive, standardized sentence structures and low lexical diversity. While AEGIS handles legal genres through specialized calibration, such documents must be analyzed with domain-aware context.

### 3. Extremely Short Texts (< 60 words)
Statistical metrics such as Type-Token Ratio, Hapax Legomena, and Burstiness require an adequate sample size to establish stable variance. AEGIS enforces an inviolable system rule: texts under 60 words return `INSUFFICIENT_EVIDENCE`.

### 4. Heavy Human Rewriting (Co-Authorship)
When an author uses AI to draft ideas and substantially rewrites every sentence with idiosyncratic human phrasing, the synthetic statistical fingerprint is fundamentally altered. AEGIS classifies these cases as `AI_ASSISTED_EDITED` or `HYBRID_MIXED` rather than full AI generation.

---

## 3. Responsible Forensic Code of Conduct

1. **No Automated Disciplinary Actions:** AEGIS output must never serve as the sole justification for disciplinary action, academic dismissal, employment termination, or legal sanctions.
2. **Mandatory Human-in-the-Loop:** All forensic reports must be interpreted by qualified subject-matter experts who consider author history, drafting drafts, and document context.
3. **Transparent Uncertainty:** The 95% uncertainty interval and inter-module disagreement metrics must always be reported alongside the point estimate.

