# AEGIS Deployment Guide

## 1. Local Development Run

### Prerequisites
- Python 3.10+ (CUDA GPU optional, automatically detected)
- Node.js 18+ and npm

```bash
# 1. Start Backend (REST API + HireCrew Seller API + MCP SSE)
cd aegis/backend
pip install -r requirements.txt
python run_server.py
```
*Backend runs on `http://127.0.0.1:8000`.*

```bash
# 2. Start Frontend Forensic Dashboard
cd aegis/frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:5173`.*

---

## 2. Docker Deployment

AEGIS provides multi-container Docker orchestration for unified deployment:

```bash
cd aegis/docker
docker-compose up --build -d
```

### Services Started:
- **`aegis_backend`**: Exposes FastAPI REST API, HireCrew adapter, and MCP server on port `8000`.
- **`aegis_frontend`**: Production NGINX web server serving the React dashboard on port `3000`.

---

## 3. Public Production Deployment (Cloud Hosting)

To deploy AEGIS as a public seller endpoint for HireCrew:

### A. Deploy on Render / Railway / Fly.io / AWS
1. Push repository to GitHub (`https://github.com/Swapnil-Biswas/Aegis`).
2. Create a Web Service pointing to `docker/Dockerfile.backend`.
3. Set Environment Variables:
   ```env
   AEGIS_DEVICE=cpu
   HIRECREW_SELLER_TOKEN=your-strong-random-token
   AEGIS_DB_PATH=/data/aegis_jobs.db
   ```
4. Attach persistent disk storage for SQLite database at `/data`.
5. Note your public HTTPS URL (e.g. `https://aegis-production.up.railway.app`).
6. Your HireCrew seller endpoint is `https://aegis-production.up.railway.app/jobs`.

---

## 4. Health Checks & Telemetry

- **System Health**: `GET /api/v1/health`
- **MCP Streamable HTTP**: `GET /mcp`
- **Interactive OpenAPI Documentation**: `GET /docs`
- **HireCrew Job Polling**: `GET /jobs/{jobId}`

