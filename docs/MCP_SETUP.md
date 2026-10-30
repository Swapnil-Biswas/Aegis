# AEGIS Model Context Protocol (MCP) Setup & Integration Guide

AEGIS includes a native **Model Context Protocol (MCP v2.3.0)** implementation that exposes its multi-layer forensic detection engine to local and remote AI agents (Claude Desktop, Cursor, Antigravity, or custom MCP clients).

---

## 1. Supported MCP Transports

### A. Local STDIO Transport
Runs the MCP server locally over standard input/output.

```bash
# Direct Python launcher
cd aegis/backend
python run_mcp_stdio.py
```

#### Client Configuration (`mcpServers.json`)
Add AEGIS to your Claude Desktop or Cursor configuration:

```json
{
  "mcpServers": {
    "aegis-forensics": {
      "command": "python",
      "args": [
        "c:/Users/swapn/OneDrive/Desktop/agent/aegis/backend/run_mcp_stdio.py"
      ],
      "env": {
        "AEGIS_DEVICE": "auto",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### B. Remote Streamable HTTP / SSE Transport
Runs embedded inside the FastAPI production server on `/mcp`.

```bash
cd aegis/backend
python run_server.py
```
Endpoint: `http://localhost:8000/mcp` (or `https://your-domain.com/mcp`).

---

## 2. Available MCP Tools

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `analyze_text` | `text` (required), `analysis_depth` (`quick`, `standard`, `comprehensive`), `include_passages`, `language`, `context` | Analyzes text through all 7 forensic analytical layers. |
| `analyze_document` | `file_path`, `file_content_base64`, `filename`, `analysis_depth` | Extracts and inspects PDF, DOCX, TXT, or MD documents. |
| `analyze_passages` | `text`, `passage_window_words` (default 120), `passage_stride_words` (default 50) | Decomposes text into overlapping sliding-window passages for hybrid detection. |
| `compare_text_samples`| `sample_a`, `sample_b` | Evaluates stylometric and statistical divergence between two texts. |
| `get_analysis_report`| `analysis_id` | Retrieves a cached report or historical job by ID. |
| `get_detector_capabilities` | None | Returns active modules, versions, languages, and ECE calibration telemetry. |
| `health_check` | None | Diagnostic health check (CUDA acceleration, database status). |

---

## 3. Available MCP Resources

- `aegis://capabilities`: System capabilities, supported genres, and operational thresholds.
- `aegis://methodology`: Mathematical formulations for perplexity, burstiness, Shannon entropy, Yule's K, and Zipf's Law.
- `aegis://limitations`: Documented epistemic boundaries, ESL considerations, and minimum word count rules.
- `aegis://model-registry`: List of active detection modules and transformer model heads.
- `aegis://evaluation-summary`: Live benchmark metrics (AUROC 1.0, ECE 0.0638, Brier 0.1885).

---

## 4. Available MCP Prompts

- `forensic_text_review`: Comprehensive investigation instructing the consuming agent to evaluate text probabilistically and avoid misconduct accusations.
- `academic_writing_review`: Tailored prompt for student and academic essays with ESL sensitivity.
- `hybrid_authorship_review`: Focuses on localized passage shifts, post-generation edits, and composite human-AI text.
- `stylometric_comparison`: Evaluates whether two text samples share the same authorial hand.
- `research_evaluation_review`: Reviews detector performance, calibration errors, and adversarial robustness.

---

## 5. Example MCP Tool Invocations

### Example: Invoking `analyze_text`
```json
{
  "name": "analyze_text",
  "arguments": {
    "text": "In today's fast-paced digital landscape, artificial intelligence plays a crucial role in transforming traditional educational methodologies. It is important to remember that technology does not merely replace the instructor; rather, it fosters a vibrant and multifaceted learning environment tailored to diverse student needs. Delving into the pedagogical implications, one observes a profound synergy between machine learning algorithms and personalized curriculum delivery. Furthermore, modern adaptive platforms provide nuanced insights into cognitive retention. Ultimately, the integration of these sophisticated systems stands as a testament to the ever-evolving nature of global education.",
    "analysis_depth": "standard",
    "include_passages": true
  }
}
```
**Sample Response Excerpt**:
```json
{
  "analysis_id": "aegis-9a4f21e0b12c",
  "classification": "AI_GENERATED",
  "calibrated_ai_likelihood": 0.884,
  "confidence": 0.82,
  "uncertainty_interval": [0.76, 0.94],
  "evidence_sufficiency": {
    "has_sufficient_evidence": true,
    "word_count": 72
  },
  "inter_module_disagreement": 0.14,
  "passage_level_findings": [
    {
      "passage_id": "passage_0",
      "ai_score": 0.884,
      "color_category": "red",
      "classification": "AI_GENERATED"
    }
  ]
}
```

