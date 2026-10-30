# AEGIS Unified API Reference

AEGIS exposes three unified API surfaces powered by the same underlying forensic detection engine:
1. **Core REST API** (`/api/v1`)
2. **HireCrew Seller API** (`/jobs`)
3. **Model Context Protocol Server** (STDIO & `/mcp`)

---

## 1. Core REST Endpoints

### `POST /api/v1/analyze`
Analyzes raw text for potential synthetic generation.
- **Request Body**:
  ```json
  {
    "text": "String content to analyze (min 60 words)",
    "operating_mode": "balanced",
    "research_mode": false
  }
  ```
- **Response**: Full forensic decomposition object (`AnalysisResponse`).

### `POST /api/v1/analyze-file`
Upload and analyze `.pdf`, `.docx`, `.txt`, or `.md` documents.
- **Multipart Form**: `file`, `operating_mode`, `research_mode`.

### `POST /api/v1/stress-test`
Simulates adversarial perturbations against submitted text.
- **Request Body**: `{"text": "...", "operating_mode": "balanced"}`.
- **Response**: Original vs perturbed scores, mean score drift ($\Delta$).

### `GET /api/v1/benchmarks`
Returns live evaluation metrics (AUROC, AUPRC, ECE, Brier score, confusion matrix) across holdout sets.

### `GET /api/v1/health`
System diagnostics and hardware acceleration info.

---

## 2. HireCrew Seller Endpoints

### `POST /jobs`
Submits a new order from HireCrew.
- **Headers**:
  - `Authorization: Bearer <HIRECREW_SELLER_TOKEN>`
  - `Idempotency-Key: <order_uuid>`
- **Request Body**:
  ```json
  {
    "orderId": "00000000-0000-4000-8000-000000000001",
    "brief": "Analyze the provided text for AI generation..."
  }
  ```
- **Response (HTTP 200)**:
  ```json
  {
    "jobId": "aegis-job-3d0edb4170c2",
    "status": "queued"
  }
  ```

### `GET /jobs/{jobId}`
Polls order progress and retrieves final report.
- **Headers**:
  - `Authorization: Bearer <HIRECREW_SELLER_TOKEN>`
- **Response (HTTP 200)**:
  ```json
  {
    "jobId": "aegis-job-3d0edb4170c2",
    "status": "delivered",
    "report": "Markdown forensic report with cited URLs...",
    "sources": [
      {
        "title": "AEGIS Architecture Specification",
        "url": "https://github.com/Swapnil-Biswas/Aegis/blob/main/docs/ARCHITECTURE.md"
      }
    ]
  }
  ```

---

## 3. MCP Server Tools

- `analyze_text(text, analysis_depth, include_passages, language, context)`
- `analyze_document(file_path, file_content_base64, filename, analysis_depth)`
- `analyze_passages(text, passage_window_words, passage_stride_words)`
- `compare_text_samples(sample_a, sample_b)`
- `get_analysis_report(analysis_id)`
- `get_detector_capabilities()`
- `health_check()`
