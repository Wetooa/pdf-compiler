import { getToken } from "./auth";

const API_URL =
  typeof process !== "undefined"
    ? process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    : "http://localhost:8000";

export interface BatchMeta {
  id: string;
  name: string;
  status: string;
  pdf_count: number;
  pdf_names: string[];
  failed_count: number;
  error: string | null;
  compiled_pdf: boolean;
  created_at: string | null;
  updated_at: string | null;
}

async function fetchWithAuth(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken();
  const headers: HeadersInit = {
    ...options.headers,
  };
  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });
  return res;
}

export async function login(password: string): Promise<{ token: string }> {
  const res = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail ?? "Invalid password");
  }
  return res.json();
}

export async function listBatches(): Promise<BatchMeta[]> {
  const res = await fetchWithAuth("/api/batches");
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail ?? "Failed to load batches");
  }
  return res.json();
}

export async function getBatch(id: string): Promise<BatchMeta> {
  const res = await fetchWithAuth(`/api/batches/${id}`);
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail ?? "Failed to load batch");
  }
  return res.json();
}

export async function createBatch(
  files: File[],
  name?: string
): Promise<BatchMeta> {
  const formData = new FormData();
  for (const f of files) {
    formData.append("files", f);
  }
  if (name != null && name.trim() !== "") {
    formData.append("name", name.trim());
  }
  const token = getToken();
  const res = await fetch(`${API_URL}/api/batches`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
    credentials: "include",
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail ?? "Upload failed");
  }
  return res.json();
}

export async function deleteBatch(id: string): Promise<void> {
  const res = await fetchWithAuth(`/api/batches/${id}`, { method: "DELETE" });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail ?? "Failed to delete batch");
  }
}

export async function downloadCompiledPdf(id: string): Promise<void> {
  const res = await fetchWithAuth(`/api/batches/${id}/compiled`);
  if (!res.ok) throw new Error("Failed to download PDF");
  const blob = await res.blob();
  const disposition = res.headers.get("Content-Disposition");
  const match = disposition?.match(/filename="?([^";]+)"?/);
  const filename = match ? match[1] : `${id}-compiled.pdf`;
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export async function openSourcePdf(id: string, filename: string): Promise<void> {
  const res = await fetchWithAuth(
    `/api/batches/${id}/pdfs/${encodeURIComponent(filename)}`
  );
  if (!res.ok) throw new Error("Failed to load PDF");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  window.open(url, "_blank", "noopener,noreferrer");
  setTimeout(() => URL.revokeObjectURL(url), 60000);
}
