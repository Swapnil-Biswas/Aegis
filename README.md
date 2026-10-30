# PROJECT AEGIS
## Advanced AI-Generated Text Detection & Forensic Analysis System

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CUDA%20Accelerated-EE4C2C.svg)](https://pytorch.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

AEGIS is an enterprise-grade forensic analysis engine engineered to detect, attribute, and decompose AI-generated, human-written, and hybrid/mixed content. Rather than relying on a single classifier or uncalibrated perplexity heuristic, AEGIS evaluates text through **seven independent analytical layers**, calibrated Bayesian ensemble fusion, and semantic sliding-window passage segmentation.

---

## Key Capabilities

- **Multi-Layer Forensic Architecture**:
  - **Module A: Statistical Linguistics**: Perplexity proxy, sentence burstiness ($B = \sigma / \mu$), Shannon entropy, length-normalized lexical diversity (Root TTR, Hapax Legomena, Yule's Characteristic K), Zipfian rank fit, and n-gram repetition indexes.
  - **Module B: Stylometric Fingerprinting**: Syntactic clause complexity, function word trajectories, punctuation entropy, sentence-opening diversity, and contraction density.
  - **Module C: Neural Classifier Engine**: High-dimensional transformer latent sequence projections with temperature-scaled posterior outputs.
  - **Module D: Semantic & Discourse Analysis**: Sentence-to-sentence cosine similarity, semantic smoothness corridor index, and tautological conclusion redundancy checks.
  - **Module E: AI Generation Patterns**: Scans for model hallmark n-grams (*"delve into"*, *"testament to"*, *"tapestry of"*), formulaic transitions, and neutral "both sides" hedging templates.
  - **Module F: Discontinuity & Hybrid Slicing**: Inter-passage Jensen-Shannon Divergence ($D_{\text{JS}}$) to detect and localize authorial transitions in mixed human-AI documents.
  - **Module G: Adversarial Attack Simulator**: Stress-tests text against synonym substitutions, clause restructuring, human post-editing noise, and back-translation smoothing.
- **Passage-Level Heatmap Matrix**: Overlapping sliding-window chunker (120w window, 50w stride) with color-coded passage attribution:
  - 🟩 **Green**: Evidence consistent with authentic human writing.
  - 🟥 **Red**: Evidence consistent with synthetic AI generation.
  - 🟨 **Yellow**: Mixed or uncertain evidence.
  - ⬜ **Gray**: Insufficient word evidence ($< 35$ words).
- **Calibrated Ensemble & Threshold Profiles**:
  - **High-Precision Profile**: Prioritizes False Positive Rate $< 1\%$ for formal investigations.
  - **Balanced Profile**: Equal error rate optimization for general editorial auditing.
  - **Exploratory Screening Profile**: Sensitive flagger for candidate text inspection.
  - **Inconclusive & Insufficient Evidence Safeguards**: Non-negotiable refusal to fabricate classifications on texts under 60 words or with high inter-module discordance.
- **Forensic Explanation Engine**: Structured, non-fabricated audit reports strictly separating computed empirical facts, statistical correlations, model predictions, and epistemic limitations.
- **Multi-Format Ingestion**: Native parsing for `.txt`, `.pdf` (via pypdf), and `.docx` (via python-docx) with MIME magic verification and file size safety bounds.

---

## Project Structure

```
aegis/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints.py          # REST endpoints (/analyze, /analyze-file, /stress-test, /benchmarks, /health)
│   │   │   └── models.py             # Pydantic schemas
│   │   ├── core/
│   │   │   ├── preprocessor.py       # Sentence/passage boundary segmentation & character offset tracker
│   │   │   ├── file_parser.py        # PDF, DOCX, TXT secure ingestion
│   │   │   ├── calibrator.py         # Platt/temperature scaling & ECE validation
│   │   │   └── explanation.py        # Forensic audit report assembler
│   │   ├── detectors/
│   │   │   ├── base.py               # Abstract BaseDetector interface
│   │   │   ├── statistical.py        # Module A: Perplexity, burstiness, entropy, Zipf, TTR, Yule's K
│   │   │   ├── stylometric.py        # Module B: Clauses, function words, punctuation entropy, contractions
│   │   │   ├── neural.py             # Module C: PyTorch neural sequence classifier
│   │   │   ├── semantic.py           # Module D: Discourse cohesion, semantic smoothness, conclusion redundancy
│   │   │   ├── pattern_analyzer.py   # Module E: AI hallmark n-grams and boilerplate framing
│   │   │   └── discontinuity.py      # Module F: Sliding-window JSD divergence & hybrid transition locator
│   │   ├── ensemble/
│   │   │   ├── fusion.py             # Bayesian stacking & missing module fallback
│   │   │   └── thresholds.py         # 3 operational profiles & 7 verdict categories
│   │   ├── evaluation/
│   │   │   ├── metrics.py            # AUROC, AUPRC, ECE, Brier, FPR, Specificity
│   │   │   ├── benchmark.py          # Benchmark runner on multi-domain holdout sets
│   │   │   └── adversarial.py        # Module G: Perturbation generators & drift calculators
│   │   ├── data/
│   │   │   └── curated_benchmarks.json  # Multi-genre, multi-model evaluation corpus
│   │   ├── config.py                 # Application configuration & length limits
│   │   └── main.py                   # FastAPI application initialization
│   ├── tests/
│   │   ├── test_all_modules.py       # Comprehensive unit test suite
│   │   └── test_api_endpoints.py    # Integration test suite
│   ├── requirements.txt              # Backend dependencies
│   └── run_server.py                 # Backend launcher
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx            # Navigation, operational profile selector, CUDA badge
│   │   │   ├── TextInputArea.tsx     # Text editor, preset benchmark loader, file uploader
│   │   │   ├── VerdictBanner.tsx     # Likelihood gauge, 95% posterior interval, confidence badge
│   │   │   ├── PassageHeatmap.tsx    # Interactive sliding-window passage viewer with inspector
│   │   │   ├── ModuleBreakdown.tsx   # 6 analytical layer cards with contradiction callouts
│   │   │   ├── AdversarialStressView.tsx # Module G attack simulator with drift telemetry
│   │   │   ├── BenchmarkDashboard.tsx    # Empirical evaluation dashboard with confusion matrix
│   │   │   ├── ResearchDiagnosticsView.tsx # Deep feature matrix & raw logits viewer
│   │   │   └── ForensicReportModal.tsx   # Structured audit report modal with JSON export
│   │   ├── api.ts                    # Backend client functions
│   │   ├── types.ts                  # TypeScript interface contracts
│   │   └── App.tsx                   # Main dashboard application
│   └── package.json                  # Frontend dependencies
├── docker/
│   ├── Dockerfile.backend            # Production backend container
│   ├── Dockerfile.frontend           # Production frontend container
│   └── docker-compose.yml            # Multi-service container orchestration
└── docs/
    ├── ARCHITECTURE.md               # Technical architecture & dataflow diagrams
    ├── RESEARCH_METHODOLOGY.md       # Mathematical formulations & linguistic references
    ├── FORENSIC_VALIDATION.md        # Benchmark metrics, holdout scores, adversarial drift
    └── LIMITATIONS.md                # Epistemic boundaries & responsible use policy
```

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (CUDA GPU optional, automatically detected)
- Node.js 18+ and npm

### 2. Backend Setup
```bash
cd aegis/backend
pip install -r requirements.txt
python run_server.py
```
*Backend runs on `http://127.0.0.1:8000` (Interactive Swagger API documentation available at `http://127.0.0.1:8000/docs`).*

### 3. Frontend Setup
```bash
cd aegis/frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:5173` (or port 3000).*

### 4. Running via Docker Compose
```bash
cd aegis/docker
docker-compose up --build
```

---

## Running Verification & Tests

### Backend Unit & Integration Tests
```bash
cd aegis/backend
python -m unittest tests/test_all_modules.py
python -m unittest tests/test_api_endpoints.py
```

### Scientific Benchmark Suite
```bash
cd aegis/backend
python -m app.evaluation.benchmark
```

### Frontend Typecheck & Build
```bash
cd aegis/frontend
npm run build
```

---

## Forensic Integrity Code

1. **Probabilistic Nature**: All scores represent statistical likelihoods, not certainty.
2. **Never Fabricate Evidence**: All generated observations map to computed metrics.
3. **No Uncalibrated Scores**: Softmax logits undergo temperature and Platt scaling.
4. **Mandatory Human-in-the-Loop**: Tool outputs must accompany human editorial review.

