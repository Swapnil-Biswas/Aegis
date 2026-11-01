# PROJECT AEGIS
## Advanced AI-Generated Text Detection & Forensic Analysis System
### With Model Context Protocol (MCP) & HireCrew Marketplace Seller Integration

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-v2.3.0%20Compliant-blueviolet.svg)](https://modelcontextprotocol.io/)
[![HireCrew](https://img.shields.io/badge/HireCrew-Seller--Hosted%20Ready-success.svg)](https://hirecrew.si)
[![PyTorch](https://img.shields.io/badge/PyTorch-CUDA%20Accelerated-EE4C2C.svg)](https://pytorch.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

AEGIS is an enterprise-grade forensic analysis engine engineered to detect, attribute, and decompose AI-generated, human-written, and hybrid/mixed content. Rather than relying on a single classifier or uncalibrated perplexity heuristic, AEGIS evaluates text through **seven independent analytical layers**, a logistic stacking ensemble fitted on labelled data, and semantic sliding-window passage segmentation.

AEGIS supports direct REST interaction, an interactive React frontend, full **Model Context Protocol (MCP)** integration for Claude Desktop / Cursor, and native compliance with the **HireCrew Marketplace** (`seller-hosted-api-v1`).

---
## Key Capabilities

- **Multi-Layer Forensic Architecture**:
  - **Module A: Statistical Linguistics**: Perplexity proxy, sentence burstiness ($B = \sigma / \mu$), Shannon entropy, length-normalized lexical diversity (Root TTR, Hapax Legomena, Yule's Characteristic K), Zipfian rank fit, and n-gram repetition indexes.
  - **Module B: Stylometric Fingerprinting**: Syntactic clause complexity, function word trajectories, punctuation entropy, sentence-opening diversity, and contraction density.
  - **Module C: Neural Classifier Engine**: Fine-tuned RoBERTa AI-text classifier (`fakespot-ai/roberta-base-ai-text-detection-v1`) applied over 512-token windows.
  - **Module H: Language-Model Perplexity**: Zero-shot token likelihood and entropy under `HuggingFaceTB/SmolLM2-135M`.
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
- **Official Model Context Protocol (MCP) Server**:
  - Exposes 7 tools, 5 read-only resources (`aegis://*`), and 5 calibrated forensic prompts.
  - Supports both **Local STDIO Transport** and **Streamable HTTP / SSE Transport** mounted at `/mcp`.
- **HireCrew Marketplace Seller Agent**:
  - Full adherence to `seller-hosted-api-v1` (`POST /jobs`, `GET /jobs/{jobId}`) with Bearer authentication and SQLite WAL persistence.
  - Non-detection briefs (research questions, recommendations, etc.) receive an explicit scope notice instead of fabricated answers.

---

## Project Structure

```
aegis/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints.py          # REST endpoints (/analyze, /analyze-file, /stress-test, /health)
│   │   │   └── models.py             # FastAPI Pydantic schemas
│   │   ├── core/
│   │   │   ├── preprocessor.py       # Sentence/passage boundary segmentation & offset tracker
│   │   │   ├── file_parser.py        # PDF, DOCX, TXT secure ingestion
│   │   │   ├── calibrator.py         # Platt/temperature scaling & ECE validation
│   │   │   └── explanation.py        # Forensic audit report assembler
│   │   ├── detectors/
│   │   │   ├── base.py               # Abstract BaseDetector interface
│   │   │   ├── statistical.py        # Module A: Perplexity, burstiness, entropy, Zipf, TTR, Yule's K
│   │   │   ├── stylometric.py        # Module B: Clauses, function words, punctuation entropy, contractions
│   │   │   ├── neural.py             # Module C: Fine-tuned RoBERTa AI-text classifier
│   │   │   ├── perplexity.py         # Module H: Language-model perplexity (SmolLM2-135M)
│   │   │   ├── registry.py           # Shared detector instances (weights loaded once)
│   │   │   ├── semantic.py           # Module D: Discourse cohesion, semantic smoothness, redundancy
│   │   │   ├── pattern_analyzer.py   # Module E: AI hallmark n-grams and boilerplate framing
│   │   │   └── discontinuity.py      # Module F: Sliding-window JSD divergence & hybrid locator
│   │   ├── ensemble/
│   │   │   ├── fusion.py             # Logistic stacking with fallback tiers for missing modules
│   │   │   └── thresholds.py         # 3 operational profiles & 7 verdict categories
│   │   ├── evaluation/
│   │   │   ├── metrics.py            # AUROC, AUPRC, ECE, Brier, FPR, Specificity
│   │   │   ├── benchmark.py          # Runner for the small curated sample set
│   │   │   ├── fit_fusion.py         # Fits fusion weights + measures held-out metrics on public data
│   │   │   └── adversarial.py        # Module G: Perturbation generators & drift calculators
│   │   ├── db/
│   │   │   └── jobs.py               # SQLite WAL job persistence & idempotency engine
│   │   ├── hirecrew/
│   │   │   ├── models.py             # HireCrew API v1 request/response schemas
│   │   │   ├── brief_parser.py       # Adversarial prompt-injection safe brief parser
│   │   │   ├── worker.py             # Async job processor & authoritative source verifier
│   │   │   └── routes.py             # Seller endpoints (POST /jobs, GET /jobs/{jobId})
│   │   ├── mcp/
│   │   │   └── server.py             # Official MCP SDK (v2.3.0) tools, resources & prompts
│   │   ├── data/
│   │   │   ├── curated_benchmarks.json  # Multi-genre, multi-model evaluation corpus
│   │   │   ├── fusion_weights.json      # Fitted stacking coefficients
│   │   │   ├── evaluation_summary.json  # Measured held-out metrics (served via MCP)
│   │   │   └── hirecrew_benchmark_outputs.json # Local research-v1 run outputs (scope notices)
│   │   ├── config.py                 # Configuration, operating limits & auth secrets
│   │   └── main.py                   # FastAPI initialization & /mcp SSE mount
│   ├── tests/
│   │   ├── test_all_modules.py       # Core detection unit tests
│   │   ├── test_api_endpoints.py     # FastAPI REST endpoint integration tests
│   │   ├── test_mcp.py               # MCP tools, resources, and prompt tests
│   │   └── test_hirecrew.py          # HireCrew seller API & idempotency tests
│   ├── run_mcp_stdio.py              # Dedicated STDIO MCP server entry point
│   ├── run_hirecrew_benchmark_eval.py# HireCrew research-v1 runner
│   ├── validate_against_hirecrew.ts  # Validation script using HireCrew seller-local kit
│   ├── requirements.txt              # Backend dependencies
│   └── run_server.py                 # Backend launcher
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx            # Navigation, profile selector, hardware badge
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
├── docs/
│   ├── ARCHITECTURE.md               # Technical architecture & multi-layer engine flow
│   ├── AUDIT_AND_ARCHITECTURE_PHASE2.md # Phase 2 MCP & HireCrew integration audit
│   ├── API_REFERENCE.md              # Unified REST, MCP, and HireCrew endpoint reference
│   ├── MCP_SETUP.md                  # Comprehensive MCP STDIO & HTTP setup guide
│   ├── HIRECREW_INTEGRATION.md       # HireCrew platform seller-hosted integration guide
│   ├── HIRECREW_LISTING.md           # Marketplace listing copy & reviewer instructions
│   ├── RESEARCH_METHODOLOGY.md       # Mathematical formulations & linguistic references
│   ├── FORENSIC_VALIDATION.md        # Benchmark metrics, holdout scores, adversarial drift
│   ├── SECURITY.md                   # Threat model, prompt injection & SSRF defenses
│   ├── ENVIRONMENT.md                # Environment variable matrix & configuration profiles
│   └── LIMITATIONS.md                # Epistemic boundaries & responsible use policy
├── hirecrew_manifest.json            # Validated HireCrew deployment manifest
└── mcpServers.json                   # Ready-to-use Cursor / Claude Desktop configuration
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
*Backend runs on `http://127.0.0.1:8000` (Swagger UI at `http://127.0.0.1:8000/docs`).*

### 3. Frontend Setup
```bash
cd aegis/frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:5173`.*

---

## Model Context Protocol (MCP) Usage

### Connecting to Claude Desktop / Cursor (STDIO)
Add the following to your `claude_desktop_config.json` or Cursor MCP settings (also available in [`mcpServers.json`](mcpServers.json)):

```json
{
  "mcpServers": {
    "aegis-forensics": {
      "command": "python",
      "args": [
        "<PATH_TO_AEGIS>/backend/run_mcp_stdio.py"
      ],
      "env": {
        "AEGIS_DEVICE": "cpu",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Remote Streamable HTTP / SSE Transport
The MCP server is also mounted directly at `/mcp` on the FastAPI server:
```bash
# Connect an SSE MCP client to:
http://127.0.0.1:8000/mcp
```

For complete MCP tool parameter schemas, resource URIs, and prompt descriptions, see [`docs/MCP_SETUP.md`](docs/MCP_SETUP.md).

---

## HireCrew Marketplace Integration

AEGIS operates as an independent seller-hosted agent on HireCrew (`https://hirecrew.si`):

1. **Submit Job**:
   ```http
   POST /jobs
   Authorization: Bearer <HIRECREW_SELLER_TOKEN>
   Idempotency-Key: <unique-uuid>
   Content-Type: application/json

   {
     "orderId": "order-12345",
     "buyerId": "buyer-67890",
     "brief": "Analyze the following paper for AI authorship: [Text...]"
   }
   ```
2. **Poll Result**:
   ```http
   GET /jobs/{jobId}
   Authorization: Bearer <HIRECREW_SELLER_TOKEN>
   ```
   Returns `status: "delivered"` with structured report markdown and authoritative sources cited.

3. **Scope**: AEGIS only performs AI-authorship analysis. HireCrew's research-v1 benchmark briefs (web research, fact-checks, recommendations) are answered with an honest scope notice rather than canned or fabricated research.

For full details, review [`docs/HIRECREW_INTEGRATION.md`](docs/HIRECREW_INTEGRATION.md) and [`hirecrew_manifest.json`](hirecrew_manifest.json).

---

## Running Verification & Tests

### Complete Backend Test Suite
```bash
cd aegis/backend
python -m unittest discover tests
```

### HireCrew Local Builder Kit Validation
```bash
cd aegis
node "<PATH_TO_HIRECREW>/platform/node_modules/tsx/dist/cli.mjs" backend/validate_against_hirecrew.ts
```

### Frontend Production Build
```bash
cd aegis/frontend
npm run build
```

---

## Forensic Integrity Code

1. **Probabilistic Nature**: All scores represent calibrated statistical likelihoods ($p \in [0, 1]$), never absolute claims of authorship.
2. **Never Fabricate Evidence**: Every finding maps strictly to calculated empirical features and statistical distributions.
3. **Measured, Not Asserted**: Fusion weights are fitted on public labelled data and evaluated on a held-out split (AUROC 0.987, ECE 0.048; see [`docs/FORENSIC_VALIDATION.md`](docs/FORENSIC_VALIDATION.md) for caveats and out-of-distribution results).
4. **Epistemic Humility**: Mandatory refusal (`INSUFFICIENT_EVIDENCE`) for texts $< 60$ words and explicit `INCONCLUSIVE` output during inter-module discordance.
5. **Mandatory Human-in-the-Loop**: Forensic outputs serve as advisory evidence to aid human professional judgment.
