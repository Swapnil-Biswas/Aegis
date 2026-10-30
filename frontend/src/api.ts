import type {
  AnalysisResponse,
  StressTestResponse,
  BenchmarkResponse,
  SystemHealth,
  OperatingMode,
} from "./types";

const API_BASE = "http://127.0.0.1:8000/api/v1";

export async function analyzeText(
  text: string,
  mode: OperatingMode = "balanced",
  researchMode: boolean = false
): Promise<AnalysisResponse> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      operating_mode: mode,
      research_mode: researchMode,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error: ${res.statusText}`);
  }

  return res.json();
}

export async function analyzeFile(
  file: File,
  mode: OperatingMode = "balanced",
  researchMode: boolean = false
): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("operating_mode", mode);
  formData.append("research_mode", String(researchMode));

  const res = await fetch(`${API_BASE}/analyze-file`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error: ${res.statusText}`);
  }

  return res.json();
}

export async function runStressTest(
  text: string,
  mode: OperatingMode = "balanced"
): Promise<StressTestResponse> {
  const res = await fetch(`${API_BASE}/stress-test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      operating_mode: mode,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error: ${res.statusText}`);
  }

  return res.json();
}

export async function getBenchmarks(mode: OperatingMode = "balanced"): Promise<BenchmarkResponse> {
  const res = await fetch(`${API_BASE}/benchmarks?mode=${mode}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch benchmark metrics: ${res.statusText}`);
  }
  return res.json();
}

export async function getSystemHealth(): Promise<SystemHealth> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.statusText}`);
  }
  return res.json();
}
