# AEGIS Environment & Configuration Reference

This document details all environment variables and configuration options used to customize the AEGIS detection engine, the FastAPI server, the MCP server, and the HireCrew seller adapter.

---

## 1. Environment Variable Reference Matrix

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `AEGIS_HOST` | `string` | `0.0.0.0` | Bind host address for FastAPI server. |
| `AEGIS_PORT` | `integer` | `8000` | Port for FastAPI / HTTP MCP server. |
| `AEGIS_DEVICE` | `string` | `auto` | Execution device for neural models (`auto`, `cuda`, `cpu`). If `auto`, selects CUDA if available. |
| `AEGIS_DB_PATH` | `string` | `backend/app/data/aegis_jobs.db` | Absolute or relative file path to the SQLite persistence database. |
| `HIRECREW_SELLER_TOKEN` | `string` | `aegis-hirecrew-seller-token-secret` | Shared secret token required for `Authorization: Bearer <token>` on `/jobs` endpoints. |
| `AEGIS_MCP_TOKEN` | `string` | *(unset / None)* | Optional bearer token protecting the remote Streamable HTTP MCP endpoint (`/mcp`). |
| `AEGIS_LOG_LEVEL` | `string` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `AEGIS_EPHEMERAL_MODE` | `boolean` | `false` | When `true`, raw text bodies are scrubbed from memory and database after score generation. |
| `PYTHONUNBUFFERED` | `integer` | `1` | Forces unbuffered stdout/stderr streams (essential for STDIO MCP transport). |

---

## 2. Threshold & Calibration Parameters

Operating thresholds are defined in `aegis/backend/app/config.py` and can be customized within the `AegisConfig` class:

### 2.1 Risk Profile Cutoffs
- **High-Precision Mode (Default)**:
  - `high_precision_ai_cutoff = 0.82`: Minimum probability required to classify as `LIKELY_AI_GENERATED`.
  - `high_precision_human_cutoff = 0.20`: Maximum probability allowed for `LIKELY_HUMAN_WRITTEN`.
- **Inconclusive Interval**:
  - `inconclusive_low = 0.40`
  - `inconclusive_high = 0.60`
  - Values falling in `[0.40, 0.60]` produce an `INCONCLUSIVE` verdict under Rule 8.
- **Inter-Module Disagreement**:
  - `inter_module_disagreement_threshold = 0.18`
  - If module variance exceeds 0.18, the system flags discordant evidence and lowers overall confidence.

### 2.2 Text Length Thresholds
- `min_word_count_insufficient = 60`: Texts shorter than 60 words trigger Rule 7 (`INSUFFICIENT_EVIDENCE`).
- `min_word_count_low_confidence = 150`: Texts between 60 and 150 words receive reduced confidence caps.
- `min_word_count_optimal = 300`: Full multi-layer forensic battery activates.

---

## 3. Configuration Profiles

### 3.1 Local Development Profile (`.env.development`)
```bash
# General
AEGIS_HOST=127.0.0.1
AEGIS_PORT=8000
AEGIS_DEVICE=auto
AEGIS_LOG_LEVEL=DEBUG

# Storage
AEGIS_DB_PATH=./app/data/aegis_jobs.db

# Authentication
HIRECREW_SELLER_TOKEN=dev-secret-token-12345
AEGIS_MCP_TOKEN=
```

### 3.2 Production Deployment Profile (`.env.production`)
```bash
# General
AEGIS_HOST=0.0.0.0
AEGIS_PORT=8000
AEGIS_DEVICE=cuda
AEGIS_LOG_LEVEL=INFO

# Storage (Persistent Volume)
AEGIS_DB_PATH=/data/aegis_jobs.db

# Security & Marketplace Auth
HIRECREW_SELLER_TOKEN=sk-live-aegis-hirecrew-994b7a1e8c0
AEGIS_MCP_TOKEN=mcp-live-token-77f920da821
AEGIS_EPHEMERAL_MODE=false
```

### 3.3 MCP STDIO Client Configuration (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "aegis-forensics": {
      "command": "python",
      "args": [
        "c:/Users/swapn/OneDrive/Desktop/agent/aegis/backend/run_mcp_stdio.py"
      ],
      "env": {
        "AEGIS_DEVICE": "cpu",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

---

## 4. Verification

To verify that your environment variables are correctly loaded and active:
```bash
cd aegis/backend
python -c "from app.config import config; print('Device:', config.device, '| DB:', config.database_path)"
```
Expected output:
```text
Device: cuda | DB: c:\Users\...\aegis\backend\app\data\aegis_jobs.db
```

