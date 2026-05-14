import { RefreshCcw } from "lucide-react";
import { useEffect, useState } from "react";
import { activatePromptVersion, listPromptVersions, type PromptVersion } from "../api/client";
import { PromptVersionCard } from "../components/self-improvement/PromptVersionCard";

export function PromptVersions() {
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  const [agentName, setAgentName] = useState("");
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      setVersions(await listPromptVersions({ agent_name: agentName || undefined }));
    } finally {
      setLoading(false);
    }
  };

  const activate = async (id: number) => {
    const confirmed = window.confirm("Kích hoạt phiên bản lời nhắc này cho tác nhân tương ứng?");
    if (!confirmed) return;
    await activatePromptVersion(id);
    await load();
  };

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-white">Phiên bản lời nhắc</h1>
        <p className="mt-1 text-sm text-slate-400">Lời nhắc được tạo sẽ chưa hoạt động cho đến khi được kích hoạt rõ ràng</p>
      </header>

      <section className="grid gap-3 rounded border border-line bg-panel p-4 shadow-soft md:grid-cols-[1fr_auto]">
        <input
          className="min-h-11 rounded border border-line bg-ink px-3 text-sm text-white"
          onChange={(event) => setAgentName(event.target.value)}
          placeholder="Tên tác nhân"
          value={agentName}
        />
        <button
          className="inline-flex min-h-11 items-center justify-center gap-2 rounded bg-accent px-4 text-sm font-semibold text-ink transition hover:bg-accent/90 disabled:opacity-60"
          disabled={loading}
          onClick={() => void load()}
          type="button"
        >
          <RefreshCcw size={16} aria-hidden="true" />
          Làm mới
        </button>
      </section>

      <section className="space-y-4">
        {versions.map((version) => (
          <PromptVersionCard key={version.id} version={version} onActivate={(id) => void activate(id)} />
        ))}
        {!versions.length ? <p className="rounded border border-line bg-panel p-5 text-sm text-slate-400">Chưa có phiên bản lời nhắc.</p> : null}
      </section>
    </div>
  );
}
