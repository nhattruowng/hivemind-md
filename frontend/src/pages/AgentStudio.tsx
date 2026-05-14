import { Bot, FlaskConical, Loader2, Plus, Shield, SlidersHorizontal, Wrench, type LucideIcon } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  createPlatformAgent,
  listPlatformAgents,
  testPlatformAgent,
  type AgentRuntimeResponse,
  type PlatformAgent
} from "../api/client";

const categoryLabels: Record<string, string> = {
  core: "Core",
  knowledge: "Knowledge",
  safety: "Safety",
  personalization: "Personal",
  coding_documents: "Code & Docs",
  custom: "Custom"
};

export function AgentStudio() {
  const [agents, setAgents] = useState<PlatformAgent[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testInput, setTestInput] = useState("Tóm tắt request này và lập kế hoạch trả lời.");
  const [runtime, setRuntime] = useState<AgentRuntimeResponse | null>(null);
  const [form, setForm] = useState({
    name: "",
    role: "assistant",
    category: "custom",
    description: "",
    goal: "",
    system_prompt: "",
    risk_level: "low" as "low" | "medium" | "high"
  });

  const refresh = async () => {
    setLoading(true);
    try {
      const data = await listPlatformAgents();
      setAgents(data);
      setSelectedId((current) => current || data[0]?.id || "");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  const selected = useMemo(() => agents.find((agent) => agent.id === selectedId) ?? agents[0], [agents, selectedId]);
  const grouped = useMemo(() => {
    return agents.reduce<Record<string, PlatformAgent[]>>((acc, agent) => {
      const key = agent.category || "custom";
      acc[key] = [...(acc[key] ?? []), agent];
      return acc;
    }, {});
  }, [agents]);

  const createAgent = async (event: FormEvent) => {
    event.preventDefault();
    if (!form.name.trim()) return;
    setCreating(true);
    try {
      const created = await createPlatformAgent({
        ...form,
        goal: form.goal || form.description,
        system_prompt: form.system_prompt || `${form.name}: ${form.description}`,
        allowed_tools: [],
        evaluation_metrics: ["accuracy", "usefulness", "risk_score", "latency_ms"]
      });
      await refresh();
      setSelectedId(created.id);
      setForm({ name: "", role: "assistant", category: "custom", description: "", goal: "", system_prompt: "", risk_level: "low" });
    } finally {
      setCreating(false);
    }
  };

  const runTest = async () => {
    if (!selected) return;
    setTesting(true);
    try {
      const result = await testPlatformAgent(selected.id, {
        message: testInput,
        question: testInput,
        answer: "Runtime smoke test answer grounded by provided input.",
        retrieval: [{ file_path: "runtime/test", preview: testInput }],
        citations: [{ id: "S1", file_path: "runtime/test" }]
      });
      setRuntime(result);
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="grid gap-5 xl:grid-cols-[360px_minmax(0,1fr)]">
      <section className="space-y-4">
        <header>
          <h1 className="text-2xl font-semibold text-white">Agent Studio</h1>
          <p className="mt-1 text-sm text-slate-400">Registry, runtime test và contract của 36 agent hệ thống.</p>
        </header>

        <div className="rounded border border-line bg-panel p-4 shadow-soft">
          <div className="grid grid-cols-3 gap-2">
            <MiniStat label="Agents" value={String(agents.length)} />
            <MiniStat label="System" value={String(agents.filter((agent) => agent.is_system).length)} />
            <MiniStat label="Custom" value={String(agents.filter((agent) => !agent.is_system).length)} />
          </div>
        </div>

        <div className="max-h-[68vh] space-y-4 overflow-auto pr-1 scrollbar-thin">
          {loading ? (
            <div className="rounded border border-line bg-panel p-4 text-sm text-slate-400">Đang tải agent...</div>
          ) : (
            Object.entries(grouped).map(([category, items]) => (
              <div key={category} className="rounded border border-line bg-panel p-3">
                <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  {categoryLabels[category] ?? category}
                </div>
                <div className="space-y-2">
                  {items.map((agent) => (
                    <button
                      key={agent.id}
                      className={[
                        "w-full rounded border p-3 text-left transition",
                        selected?.id === agent.id ? "border-signal bg-signal/10" : "border-line bg-ink hover:bg-white/5"
                      ].join(" ")}
                      type="button"
                      onClick={() => {
                        setSelectedId(agent.id);
                        setRuntime(null);
                      }}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div className="min-w-0 truncate text-sm font-semibold text-white">{agent.name}</div>
                        <RiskBadge value={agent.risk_level} />
                      </div>
                      <div className="mt-1 truncate text-xs text-slate-400">{agent.role}</div>
                    </button>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      <main className="space-y-5">
        {selected ? <AgentDetail agent={selected} /> : null}

        <section className="rounded border border-line bg-panel p-4 shadow-soft">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h2 className="text-sm font-semibold text-white">Runtime test</h2>
              <p className="mt-1 text-xs text-slate-400">Agent có adapter thật sẽ chạy; agent chưa có adapter trả trạng thái skipped có audit timeline.</p>
            </div>
            <button
              className="inline-flex min-h-10 items-center justify-center gap-2 rounded bg-accent px-4 text-sm font-semibold text-ink disabled:opacity-50"
              disabled={!selected || testing}
              type="button"
              onClick={() => void runTest()}
            >
              {testing ? <Loader2 size={16} className="animate-spin" aria-hidden="true" /> : <FlaskConical size={16} aria-hidden="true" />}
              Test
            </button>
          </div>
          <textarea
            className="mt-3 min-h-24 w-full resize-y rounded border border-line bg-ink px-3 py-2 text-sm leading-6 text-white"
            value={testInput}
            onChange={(event) => setTestInput(event.target.value)}
          />
          {runtime ? <RuntimePanel runtime={runtime} /> : null}
        </section>

        <section className="rounded border border-line bg-panel p-4 shadow-soft">
          <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
            <Plus size={16} className="text-signal" aria-hidden="true" />
            Create custom agent
          </div>
          <form className="grid gap-3 md:grid-cols-2" onSubmit={createAgent}>
            <Field label="Name" value={form.name} onChange={(value) => setForm({ ...form, name: value })} />
            <Field label="Role" value={form.role} onChange={(value) => setForm({ ...form, role: value })} />
            <Field label="Category" value={form.category} onChange={(value) => setForm({ ...form, category: value })} />
            <label className="text-xs text-slate-400">
              Risk
              <select
                className="mt-1 min-h-10 w-full rounded border border-line bg-ink px-3 text-sm text-white"
                value={form.risk_level}
                onChange={(event) => setForm({ ...form, risk_level: event.target.value as "low" | "medium" | "high" })}
              >
                <option value="low">low</option>
                <option value="medium">medium</option>
                <option value="high">high</option>
              </select>
            </label>
            <label className="md:col-span-2 text-xs text-slate-400">
              Description
              <textarea
                className="mt-1 min-h-20 w-full rounded border border-line bg-ink px-3 py-2 text-sm leading-6 text-white"
                value={form.description}
                onChange={(event) => setForm({ ...form, description: event.target.value })}
              />
            </label>
            <button
              className="inline-flex min-h-10 items-center justify-center gap-2 rounded border border-signal px-4 text-sm font-semibold text-signal hover:bg-signal/10 disabled:opacity-50 md:col-span-2"
              disabled={creating || !form.name.trim()}
              type="submit"
            >
              {creating ? <Loader2 size={16} className="animate-spin" aria-hidden="true" /> : <Bot size={16} aria-hidden="true" />}
              Create agent
            </button>
          </form>
        </section>
      </main>
    </div>
  );
}

function AgentDetail({ agent }: { agent: PlatformAgent }) {
  return (
    <section className="rounded border border-line bg-panel p-5 shadow-soft">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded border border-signal/30 bg-signal/10 px-2 py-1 text-xs font-semibold text-signal">
              {categoryLabels[agent.category] ?? agent.category}
            </span>
            <RiskBadge value={agent.risk_level} />
            {agent.is_system ? <span className="rounded border border-line px-2 py-1 text-xs text-slate-400">system</span> : null}
          </div>
          <h2 className="mt-3 text-2xl font-semibold text-white">{agent.name}</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">{agent.description || agent.goal}</p>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs lg:w-[360px]">
          <Info label="Role" value={agent.role} />
          <Info label="Model" value={agent.default_model || "default"} />
          <Info label="Temp" value={String(agent.temperature)} />
          <Info label="Slug" value={agent.slug} />
        </div>
      </div>

      <div className="mt-5 grid gap-3 lg:grid-cols-3">
        <ListBlock icon={Wrench} title="Allowed tools" items={agent.allowed_tools} empty="No tools" />
        <ListBlock icon={SlidersHorizontal} title="Metrics" items={agent.evaluation_metrics} empty="No metrics" />
        <ListBlock icon={Shield} title="Contract" items={Object.keys(agent.output_schema?.properties ?? {})} empty="No schema" />
      </div>
    </section>
  );
}

function RuntimePanel({ runtime }: { runtime: AgentRuntimeResponse }) {
  return (
    <div className="mt-4 space-y-3 border-t border-line pt-4">
      <div className="grid gap-2 md:grid-cols-3">
        <Info label="Task" value={runtime.task_id} />
        <Info label="Status" value={runtime.result.status} />
        <Info label="Runtime" value={formatRuntime(runtime.result.runtime_ms ?? 0)} />
      </div>
      <div className="rounded border border-line bg-ink p-3 text-xs leading-5 text-slate-300">
        {runtime.result.message}
      </div>
      <div className="space-y-2">
        {runtime.timeline.map((item, index) => (
          <div key={`${item.agent}-${index}`} className="rounded border border-line bg-ink p-3 text-xs">
            <div className="flex items-center justify-between gap-3">
              <div className="font-semibold text-white">{item.agent}</div>
              <span className="text-accent">{item.status}</span>
            </div>
            <p className="mt-1 text-slate-400">{item.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="text-xs text-slate-400">
      {label}
      <input
        className="mt-1 min-h-10 w-full rounded border border-line bg-ink px-3 text-sm text-white"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function ListBlock({ icon: Icon, title, items, empty }: { icon: LucideIcon; title: string; items: string[]; empty: string }) {
  return (
    <div className="rounded border border-line bg-ink p-3">
      <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
        <Icon size={14} aria-hidden="true" />
        {title}
      </div>
      <div className="flex flex-wrap gap-1.5">
        {(items.length ? items : [empty]).slice(0, 12).map((item) => (
          <span key={item} className="rounded border border-line bg-panel px-2 py-1 text-xs text-slate-300">
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

function RiskBadge({ value }: { value: string }) {
  const color = value === "high" ? "border-red-400/40 text-red-200" : value === "medium" ? "border-amber-300/40 text-amber-200" : "border-emerald-300/40 text-emerald-200";
  return <span className={["rounded border px-2 py-1 text-[11px] font-semibold", color].join(" ")}>{value}</span>;
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-line bg-ink px-3 py-2">
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 text-lg font-semibold text-white">{value}</div>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 rounded border border-line bg-ink px-3 py-2">
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 truncate text-sm font-semibold text-white">{value}</div>
    </div>
  );
}

function formatRuntime(value: number) {
  if (value < 1000) return `${value}ms`;
  return `${(value / 1000).toFixed(1)}s`;
}
