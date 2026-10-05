const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function checkBackendHealth(): Promise<{
  ok: boolean;
  message: string;
}> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, {
      cache: "no-store",
    });

    if (!res.ok) {
      return { ok: false, message: `HTTP ${res.status}` };
    }

    const data = await res.json();

    return { ok: true, message: JSON.stringify(data) };
  } catch (err) {
    return { ok: false, message: (err as Error).message };
  }
}