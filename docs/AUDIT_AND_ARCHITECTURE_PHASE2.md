# AEGIS Phase 2 Architecture Audit & Implementation Plan
## MCP Integration & HireCrew Seller-Hosted Agent Readiness

> **Auditor**: Senior Software Architect & Research Engineer  
> **Status**: Verified Repository Audit & Active Integration  
> **Target Platforms**: Model Context Protocol (MCP v2.3.0), HireCrew Marketplace (hirecrew.si)

---

## 1. Initial Repository Audit

### Backend Framework
- **Core**: Python 3.14 / FastAPI 0.141.1 with Starlette and Pydantic v2.
- **Compute**: PyTorch 2.11+cu128 (CUDA accelerated with NVIDIA RTX 4050 Laptop GPU fallback to CPU).
- **Processing**: Scikit-Learn 1.9, SciPy 1.18, NumPy 2.5, HashingVectorizer, TfidfVectorizer.
- **Parsers**: Native `pypdf` (PDF), `python-docx` (DOCX), and multi-encoding UTF-8/Latin-1 text reader.

### Frontend Framework
- **Core**: React 18.3, TypeScript 5, Vite 8.3.
- **Styling**: Tailwind CSS 3.4.17 with dark-mode aesthetic.
- **Icons**: Lucide-React.
- **Build Status**: Verified production build (`dist/`) in 917ms with zero type errors.

### Existing Detection Engine
All 7 independent analytical layers are fully operational:
- **Module A (Statistical Linguistics)**: Perplexity proxy, sentence burstiness ($B = \sigma/\mu$), Shannon entropy, length-normalized lexical diversity (Root TTR, Hapax Legomena, Yule's Characteristic K), Zipfian power-law exponent $\alpha$, bigram/trigram repetition.
- **Module B (Stylometric Fingerprinting)**: Syntactic clause complexity, function word trajectories, punctuation entropy, contraction density, sentence-opening diversity.
- **Module C (Neural Detection Engine)**: PyTorch latent sequence projection with temperature-scaled calibrated logits.
- **Module D (Semantic & Discourse Analysis)**: Consecutive sentence cosine trajectory, Semantic Smoothness Index, tautological conclusion redundancy checks.
- **Module E (AI Generation Patterns)**: Scans for hallmark model n-grams (*"delve into"*, *"testament to"*, *"tapestry of"*), formulaic introductions, and neutral "both sides" hedging.
- **Module F (Discontinuity & Hybrid Slicing)**: Sliding-window Jensen-Shannon Divergence ($D_{\text{JS}}$) across adjacent passages with authorial boundary shift localization.
- **Module G (Adversarial Robustness)**: Stress-test harness against synonym swaps, clause inversions, human post-editing noise, and translation smoothing.

### Existing Ensemble & Calibration
- Calibrated Bayesian/Logistic fusion with missing-module graceful fallback.
- *(Superseded in v1.1: fusion is now a fitted logistic stack; see FORENSIC_VALIDATION.md for measured metrics.)*
- 3 Operating Threshold Profiles: High-Precision (FPR $< 1\%$), Balanced, Exploratory Screening.
- Strict non-negotiable rules: Inconclusive verdict on high inter-module discordance; Insufficient Evidence verdict on text under 60 words.

---

## 2. Implementation Gap Analysis & Checklist

| Component | Status | Action Required |
| :--- | :--- | :--- |
| **Detection Modules A–G** | **Implemented** | Reuse as single source of truth for both REST API, MCP, and HireCrew. |
| **Preprocessor & Boundary Slicer** | **Implemented** | Reuse across all interfaces. |
| **Explanation Engine** | **Implemented** | Format reports into plain text and Markdown citations for HireCrew. |
| **Job Persistence & Idempotency** | **Missing** | Implement lightweight, thread-safe SQLite job store (`app/db/jobs.py`). |
| **HireCrew Seller API Adapter** | **Missing** | Implement `POST /jobs` and `GET /jobs/{jobId}` adhering to HireCrew v1 contract. |
| **MCP Server (Python SDK v2.3)** | **Missing** | Implement `app/mcp/server.py` with 7 tools, 5 resources, 5 prompts. |
| **MCP Transports** | **Missing** | Implement STDIO transport runner and Streamable HTTP / SSE transport. |
| **HireCrew Builder Kit Testing** | **Discovered** | Connect to `HireCrew/platform/scripts/seller-local-mcp.ts` for self-test. |
| **Deployment & Security** | **Partially Implemented** | Add Bearer token auth, rate limiting, request validation, updated Dockerfiles. |
| **Test Suites** | **Partially Implemented** | Existing unit tests pass (13/13). Add MCP and HireCrew test suites. |

---

## 3. Architecture & Integration Plan

```
                               +-------------------------------------+
                               |          Incoming Clients           |
                               +------------------+------------------+
                                                  |
                     +----------------------------+----------------------------+
                     |                            |                            |
                     v                            v                            v
        +------------+------------+  +------------+------------+  +------------+------------+
        |   Existing REST Client  |  |    Local/Remote MCP     |  |   HireCrew Marketplace   |
        |   (Web Frontend / API)  |  |   (Cursor / Claude)     |  |  (POST /jobs, GET /poll)|
        +------------+------------+  +------------+------------+  +------------+------------+
                     |                            |                            |
                     |  /api/v1/analyze           | Tools, Resources, Prompts  | Bearer Auth & Idempotency
                     v                            v                            v
        +------------+----------------------------+----------------------------+------------+
        |                               AEGIS Gateway & Auth Core                           |
        |  - Bearer Token Verification (`HIRECREW_SELLER_TOKEN`, `AEGIS_MCP_TOKEN`)         |
        |  - Request Validation & Prompt Injection Defense                                  |
        |  - Idempotency Cache & SQLite Job Persistence (`app/db/jobs.py`)                  |
        +-----------------------------------------+-----------------------------------------+
                                                  |
                                                  v
        +-----------------------------------------+-----------------------------------------+
        |                        AEGIS Forensic Core Engine                         |
        |  - Forensic Preprocessor & Sliding-Window Passage Slicer                          |
        |  - Multi-Layer Detectors (Modules A through G)                                    |
        |  - Calibrated Bayesian Ensemble & Explanation Engine                              |
        +-----------------------------------------------------------------------------------+
```

