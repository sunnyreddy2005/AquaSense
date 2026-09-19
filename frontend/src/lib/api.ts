const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type DatasetProfile = {
  rows: number;
  columns: number;
  timestamp_column: string | null;
  consumption_column: string | null;
  context_columns: string[];
  missing_values: number;
  duplicates: number;
  quality_score: number;
};

export type DatasetResponse = {
  dataset: {
    id: string;
    filename: string;
    created_at: string;
    profile: DatasetProfile;
    cleaning: {
      original_rows: number;
      cleaned_rows: number;
      removed_rows: number;
      missing_values_fixed: number;
      duplicates_removed: number;
    };
  };
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? "The AquaSense API is unavailable.");
  }
  return response.json() as Promise<T>;
}

export function uploadDataset(file: File): Promise<DatasetResponse> {
  const body = new FormData();
  body.append("file", file);
  return request<DatasetResponse>("/api/upload", { method: "POST", body });
}

export function getDataset(): Promise<{ dataset: DatasetResponse["dataset"]; rows: Record<string, unknown>[] }> {
  return request("/api/data?limit=50");
}

export function getAnalytics(): Promise<Record<string, unknown>> {
  return request("/api/analytics");
}

export function getAnomalies(): Promise<Record<string, unknown>> {
  return request("/api/anomalies");
}

export function getForecast(horizon: number, frequency = "D"): Promise<Record<string, unknown>> {
  return request("/api/forecast", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ horizon, frequency }),
  });
}

export function askAnalyst(question: string): Promise<{ answer: string }> {
  return request("/api/ai/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}

export function getReport(): Promise<Record<string, unknown>> {
  return request("/api/reports");
}

export function getSettings(): Promise<Record<string, unknown>> {
  return request("/api/settings");
}

export function saveSettings(settings: Record<string, unknown>): Promise<Record<string, unknown>> {
  return request("/api/settings", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(settings),
  });
}

export { API_URL };