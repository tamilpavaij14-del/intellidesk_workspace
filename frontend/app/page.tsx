import { checkBackendHealth } from "../utils/api";
export default async function Home() {
  const health = await checkBackendHealth();

  return (
    <main style={{ padding: 32 }}>
      <h1>IntelliDesk</h1>

      <p>
        {health.ok
          ? `Backend reachable — ${health.message}`
          : `Backend unreachable — ${health.message}`}
      </p>
    </main>
  );
}
