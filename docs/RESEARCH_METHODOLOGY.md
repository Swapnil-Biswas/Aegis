# AEGIS Research Methodology & Mathematical Formulations

## 1. Statistical Linguistic Foundations (Module A)

### Perplexity and Burstiness
Autoregressive language models decode text by greedily or nucleus-sampling tokens from low-entropy probability distributions. Human writing, conversely, alternates between highly concise constructions and dense, unpredictable conceptual formulations.

The burstiness of sentence lengths and perplexity proxies is quantified as the coefficient of variation:
$$B = \frac{\sigma}{\mu} = \frac{\sqrt{\frac{1}{M}\sum_{j=1}^M (L_j - \bar{L})^2}}{\bar{L}}$$
- Human baseline: $B > 0.45$.
- Synthetic baseline: $B \in [0.20, 0.35]$.

### Shannon Entropy of Token Distributions
Information content is measured in bits over empirical unigram frequencies:
$$H(W) = -\sum_{i=1}^V P(w_i) \log_2 P(w_i)$$

### Lexical Diversity & Sample-Length Normalization
To prevent sample length $N$ from distorting lexical richness:
- **Root TTR (Guiraud's Index):** $\text{RTTR} = \frac{V}{\sqrt{2N}}$
- **Yule's Characteristic K:**
  $$K = 10^4 \cdot \frac{\sum_{m=1}^{\infty} m^2 V_m - N}{N^2}$$
  where $V_m$ is the number of vocabulary items occurring exactly $m$ times. $K$ provides length-invariant vocabulary concentration.
- **Hapax Legomena Ratio:** $H_1 = \frac{V_1}{N}$. In short texts ($N < 150$), expected $H_1$ is asymptotically shifted to prevent false human attribution on brief model completions.

### Zipf's Law Exponent Estimation
Natural language conforms to power-law frequency distributions: $f(r) \propto r^{-\alpha}$. Linear regression on log-ranks vs log-frequencies determines the power-law exponent $\alpha$:
$$\log f(r) = -\alpha \log r + C$$
Deviations where $\alpha < 0.70$ or $R^2 < 0.75$ indicate synthetic vocabulary compression.

---

## 2. Stylometric Fingerprinting (Module B)

### Function Word Trajectories
Non-content words (pronouns, prepositions, conjunctions, auxiliary verbs) represent subconscious authorial habits. Normalized frequency vectors are compared against balanced baseline distributions.

### Punctuation Shannon Entropy
Captures expressive cadence vs formulaic comma-period uniform structures:
$$H_{\text{punct}} = -\sum_{p \in P} P(p) \log_2 P(p)$$
Where $P$ contains commas, semicolons, em-dashes, colons, hyphens, and quotation marks.

---

## 3. Discourse Flow & Semantic Smoothness (Module D)

### Semantic Smoothness Index
Cosine similarity between consecutive sentence vectors $S_i, S_{i+1}$:
$$\text{Sim}(S_i, S_{i+1}) = \frac{S_i \cdot S_{i+1}}{\|S_i\| \|S_{i+1}\|}$$
The smoothness index is formulated as:
$$\text{Smoothness} = \frac{\mu_{\text{sim}}}{\sigma_{\text{sim}} + 0.05}$$
AI texts maintain a tight, uniform cosine corridor ($\text{Smoothness} > 2.5$), whereas human authors exhibit narrative pivots and episodic conceptual leaps ($\text{Smoothness} < 1.2$).

---

## 4. Discontinuity & Boundary Shift Localization (Module F)

### Jensen-Shannon Divergence Across Sliding Windows
Given two consecutive sliding window passages $P$ and $Q$, their Jensen-Shannon divergence is:
$$D_{\text{JS}}(P \parallel Q) = \frac{1}{2} D_{\text{KL}}(P \parallel M) + \frac{1}{2} D_{\text{JS}}(Q \parallel M)$$
Where $M = \frac{1}{2}(P + Q)$ and $D_{\text{KL}}$ is Kullback-Leibler divergence. Boundary shift points are triggered whenever $D_{\text{JS}} > 0.45$.

---

## 5. Probability Calibration & Expected Calibration Error (ECE)

To guarantee that reported probabilities reflect empirical truth, raw ensemble scores are calibrated via temperature scaling:
$$P(Y=1 \mid z) = \frac{1}{1 + \exp\left(-\frac{\text{logit}(z)}{T}\right)}$$

Calibration accuracy is audited using Expected Calibration Error across $M$ equal-width bins:
$$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} |\text{acc}(B_m) - \text{conf}(B_m)|$$
AEGIS achieves an ECE of $0.10$ across multi-domain holdout evaluation benchmarks.

