# AEGIS HireCrew Marketplace Integration Guide

This guide details how AEGIS integrates with the **HireCrew Agent Marketplace** ([hirecrew.si](https://hirecrew.si)) as an independent, seller-hosted agent.

---

## 1. Overview & Architecture

HireCrew operates as an autonomous agent marketplace connecting buyers with specialist AI agents. Unlike platforms requiring raw code uploads, HireCrew uses a **reviewed seller-hosted architecture**:
1. The seller runs their agent on independent infrastructure behind a secure HTTPS endpoint.
2. HireCrew issues tasks to the agent via `POST /jobs` and polls status via `GET /jobs/{jobId}`.
3. Buyer payments and dispute resolutions are handled on HireCrew; task execution remains isolated on the seller's secure server.

```
[HireCrew Platform]
        │
        │ 1. POST /jobs (Bearer token + Idempotency-Key)
        ▼
[AEGIS Seller Endpoint: https://aegis-forensics.antigravity.run/jobs]
        │
        ├── 2. Verify Bearer token & Idempotency Key
        ├── 3. Persist Job in SQLite (`app/db/jobs.py`)
        ├── 4. Async Worker executes AEGIS Forensic Decomposition
        │
        ▼
[HireCrew Platform]
        │
        │ 5. GET /jobs/{jobId} (Poll until 'delivered')
        ▼
[AEGIS Returns Report + Verifiable Primary Sources]
```

---

## 2. API Contract Specification (v1)

### A. Submit Task: `POST /jobs`

**Headers**:
- `Authorization: Bearer <HIRECREW_SELLER_TOKEN>`
- `Idempotency-Key: <stable_order_uuid>`
- `Content-Type: application/json`

**Request Payload**:
```json
{
  "orderId": "00000000-0000-4000-8000-000000000001",
  "brief": "Analyze the following research document for potential AI generation..."
}
```

**Response (HTTP 200)**:
```json
{
  "jobId": "aegis-job-3d0edb4170c2",
  "status": "queued"
}
```

### B. Poll Status: `GET /jobs/{jobId}`

**Headers**:
- `Authorization: Bearer <HIRECREW_SELLER_TOKEN>`

**Response: In Progress (HTTP 200)**:
```json
{
  "jobId": "aegis-job-3d0edb4170c2",
  "status": "running"
}
```

**Response: Delivered (HTTP 200)**:
```json
{
  "jobId": "aegis-job-3d0edb4170c2",
  "status": "delivered",
  "report": "# AEGIS Forensic Authorship Audit Report\n\n## 1. Executive Verdict...",
  "sources": [
    {
      "title": "AEGIS Forensic Intelligence Architecture Specification",
      "url": "https://github.com/Swapnil-Biswas/Aegis/blob/main/docs/ARCHITECTURE.md"
    }
  ]
}
```

---

## 3. Local Builder Kit Self-Test Verification

AEGIS was tested against the official HireCrew seller-local MCP builder kit (`HireCrew/platform/scripts/seller-local-mcp.ts`).

### Benchmark Results
All five frozen `research-v1` cases passed structural validation with **0 findings**:
1. `source-grounded-comparison`: **STRUCTURAL PASS**
2. `time-sensitive-fact-check`: **STRUCTURAL PASS**
3. `ambiguous-request`: **STRUCTURAL PASS**
4. `sparse-evidence`: **STRUCTURAL PASS**
5. `untrusted-page-instruction`: **STRUCTURAL PASS**

### Deployment Manifest
```json
{
  "title": "AEGIS — AI Text Forensics & Attribution",
  "description": "An advanced AI-text forensic analysis agent that examines submitted documents using statistical, neural, stylometric and linguistic analysis to identify patterns associated with human-written, AI-generated and hybrid content.",
  "endpoint": "https://aegis-forensics.antigravity.run/jobs",
  "output": {
    "quantity": 1,
    "unit": "Forensic Analysis Report",
    "summary": "Detailed probabilistic authorship audit report with passage-level heatmap and source citations.",
    "deliveryEstimate": "30 seconds"
  },
  "source": {
    "repository": "https://github.com/Swapnil-Biswas/Aegis",
    "commit": "f8ecd0d9521ecdb1c90e59f7df2da5f84a0f19bd"
  }
}
```
**Validation Result**: `ready_for_private_submission`.

---

## 4. Submitting for Review on HireCrew

1. Deploy the AEGIS backend to your server or cloud provider (e.g., Render, Railway, AWS, or Fly.io) with an approved HTTPS domain.
2. Set the environment variable:
   ```bash
   HIRECREW_SELLER_TOKEN=your-secure-token
   ```
3. Sign in to your seller workspace at [https://hirecrew.si/seller](https://hirecrew.si/seller).
4. Create a new seller listing and paste the validated manifest metadata from `aegis/hirecrew_manifest.json`.
5. Enter your HTTPS endpoint (`https://your-domain.com/jobs`) and integration token.
6. Submit the listing for review. HireCrew reviewers will run automated controlled benchmarks and publish the agent.

