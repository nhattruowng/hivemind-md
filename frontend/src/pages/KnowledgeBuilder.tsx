import {
  Activity,
  ArrowRight,
  BrainCircuit,
  Clock3,
  Database,
  FileSearch,
  FileText,
  Filter,
  Gauge,
  Layers3,
  Loader2,
  Network,
  Play,
  RefreshCw,
  Route,
  Search,
  ShieldCheck,
  Workflow,
  type LucideIcon
} from "lucide-react";
import { FormEvent, type ReactNode, useEffect, useState } from "react";
import {
  buildKnowledge,
  listDomainProfiles,
  readKnowledge,
  refreshKnowledge,
  runAgentFramework,
  type BuildMode,
  type BuildKnowledgePayload,
  type DomainProfile,
  type AgentLog
} from "../api/client";
import { AgentStatusCard } from "../components/AgentStatusCard";
import { MarkdownPreview } from "../components/MarkdownPreview";
import { useAgentRun } from "../context/AgentRunContext";
import { formatValueLabel } from "../utils/labels";

export function KnowledgeBuilder() {
  const { logs, latestFile, setRun } = useAgentRun();
  const [payload, setPayload] = useState<BuildKnowledgePayload>({
    topic: "",
    category: "general",
    mode: "standard"
  });
  const [profiles, setProfiles] = useState<DomainProfile[]>([]);
  const [profileId, setProfileId] = useState("auto");
  const [loading, setLoading] = useState<"build" | "refresh" | "framework" | "">("");
  const [markdown, setMarkdown] = useState("");
  const [error, setError] = useState("");
  const [generatedFiles, setGeneratedFiles] = useState<string[]>([]);
  const [frameworkAverageScore, setFrameworkAverageScore] = useState<number | null>(null);
  const [frameworkScores, setFrameworkScores] = useState<Record<string, number>>({});
  const [frameworkStartedAt, setFrameworkStartedAt] = useState<number | null>(null);
  const [progressTick, setProgressTick] = useState(0);

  useEffect(() => {
    void listDomainProfiles().then(setProfiles).catch(() => setProfiles([]));
  }, []);

  useEffect(() => {
    if (loading !== "framework") return;
    const timer = window.setInterval(() => setProgressTick((value) => value + 1), 1000);
    return () => window.clearInterval(timer);
  }, [loading]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setMarkdown("");
    setGeneratedFiles([]);
    setFrameworkAverageScore(null);
    setFrameworkScores({});
    setLoading("build");
    try {
      const result = await buildKnowledge(payload);
      setRun(result.agent_logs, result.markdown_file);
      if (result.markdown_file) {
        const file = await readKnowledge(result.markdown_file);
        setMarkdown(file.content);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không tạo được tri thức");
    } finally {
      setLoading("");
    }
  };

  const refresh = async () => {
    setError("");
    setMarkdown("");
    setGeneratedFiles([]);
    setFrameworkAverageScore(null);
    setFrameworkScores({});
    setLoading("refresh");
    try {
      const result = await refreshKnowledge(payload);
      setRun(result.agent_logs, result.map_file);
      setGeneratedFiles(result.files);
      if (result.map_file) {
        const file = await readKnowledge(result.map_file);
        setMarkdown(file.content);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không làm mới được tri thức");
    } finally {
      setLoading("");
    }
  };

  const runFramework = async () => {
    setError("");
    setMarkdown("");
    setGeneratedFiles([]);
    setFrameworkAverageScore(null);
    setFrameworkScores({});
    setFrameworkStartedAt(Date.now());
    setProgressTick(0);
    setLoading("framework");
    try {
      const result = await runAgentFramework({ ...payload, profile_id: profileId });
      setRun(result.agent_logs, result.map_file);
      setGeneratedFiles(result.files);
      setFrameworkAverageScore(result.average_score);
      setFrameworkScores(result.agent_scores);
      if (result.map_file) {
        const file = await readKnowledge(result.map_file);
        setMarkdown(file.content);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không chạy được khung tác nhân");
    } finally {
      setLoading("");
      setFrameworkStartedAt(null);
    }
  };

  const frameworkLogs = logs.filter(
    (log) => log.stage || log.agent.startsWith("Framework") || log.agent === "KnowledgeMapService"
  );

  return (
    <div className="space-y-6">
      <section className="rounded border border-line bg-panel p-5 shadow-soft">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
          <div className="min-w-0">
            <div className="inline-flex items-center gap-2 rounded border border-signal/30 bg-signal/10 px-2.5 py-1 text-xs font-semibold text-signal">
              <BrainCircuit size={14} aria-hidden="true" />
              Knowledge Builder
            </div>
            <h1 className="mt-3 text-2xl font-semibold text-white">Tạo tri thức chuyên sâu</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Chạy tác nhân theo từng tầng: plan, search, quality, worker lanes, synthesis, filter và map Markdown.
            </p>
          </div>
          <div className="grid gap-2 sm:grid-cols-3 xl:min-w-[460px]">
            <MetricTile icon={Gauge} label="Điểm TB" value={frameworkAverageScore != null ? `${Math.round(frameworkAverageScore * 100)}%` : "N/A"} />
            <MetricTile icon={FileText} label="Markdown" value={String(generatedFiles.length || (latestFile ? 1 : 0))} />
            <MetricTile icon={Activity} label="Agent logs" value={String(logs.length)} />
          </div>
        </div>
      </section>

      <div className="grid gap-6 2xl:grid-cols-[430px_minmax(0,1fr)]">
        <aside className="space-y-4">
          <form onSubmit={submit} className="space-y-4 rounded border border-line bg-panel p-5 shadow-soft">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h2 className="text-sm font-semibold text-white">Phiên build</h2>
                <p className="mt-1 text-xs text-slate-400">Chọn topic, domain và mức xử lý.</p>
              </div>
              {loading ? (
                <span className="inline-flex items-center gap-2 rounded border border-signal/40 bg-signal/10 px-2.5 py-1 text-xs font-medium text-signal">
                  <Loader2 size={14} className="animate-spin" aria-hidden="true" />
                  {formatValueLabel(loading)}
                </span>
              ) : null}
            </div>

            <label className="block">
              <span className="text-sm font-medium text-slate-200">Chủ đề</span>
              <input
                className="mt-2 min-h-11 w-full rounded border border-line bg-ink px-3 text-sm text-white"
                value={payload.topic}
                onChange={(event) => setPayload({ ...payload, topic: event.target.value })}
                placeholder="Kiến trúc đa tác nhân cục bộ"
                required
              />
            </label>

            <div className="grid gap-3 sm:grid-cols-2 2xl:grid-cols-1">
              <label className="block">
                <span className="text-sm font-medium text-slate-200">Danh mục</span>
                <input
                  className="mt-2 min-h-11 w-full rounded border border-line bg-ink px-3 text-sm text-white"
                  value={payload.category}
                  onChange={(event) => setPayload({ ...payload, category: event.target.value })}
                  placeholder="he-thong-ai"
                  required
                />
              </label>

              <label className="block">
                <span className="text-sm font-medium text-slate-200">Chế độ</span>
                <select
                  className="mt-2 min-h-11 w-full rounded border border-line bg-ink px-3 text-sm text-white"
                  value={payload.mode}
                  onChange={(event) => setPayload({ ...payload, mode: event.target.value as BuildMode })}
                >
                  <option value="quick">{formatValueLabel("quick")}</option>
                  <option value="standard">{formatValueLabel("standard")}</option>
                  <option value="deep">{formatValueLabel("deep")}</option>
                </select>
              </label>
            </div>

            <label className="block">
              <span className="text-sm font-medium text-slate-200">Hồ sơ chuyên sâu</span>
              <select
                className="mt-2 min-h-11 w-full rounded border border-line bg-ink px-3 text-sm text-white"
                value={profileId}
                onChange={(event) => setProfileId(event.target.value)}
              >
                <option value="auto">Tự chọn theo chủ đề</option>
                {profiles.map((profile) => (
                  <option key={profile.id} value={profile.id}>
                    {profile.name}
                  </option>
                ))}
              </select>
            </label>

            <div className="grid gap-2">
              <button
                className="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded bg-accent px-4 text-sm font-semibold text-ink transition hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={Boolean(loading) || !payload.topic.trim()}
                type="submit"
              >
                {loading === "build" ? <Loader2 size={18} className="animate-spin" aria-hidden="true" /> : <Play size={18} aria-hidden="true" />}
                Tạo tri thức
              </button>

              <div className="grid gap-2 sm:grid-cols-2 2xl:grid-cols-1">
                <button
                  className="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded border border-signal px-4 text-sm font-semibold text-signal transition hover:bg-signal/10 disabled:cursor-not-allowed disabled:opacity-60"
                  disabled={Boolean(loading) || !payload.topic.trim()}
                  type="button"
                  onClick={() => void refresh()}
                >
                  {loading === "refresh" ? <Loader2 size={18} className="animate-spin" aria-hidden="true" /> : <RefreshCw size={18} aria-hidden="true" />}
                  Làm mới
                </button>

                <button
                  className="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded border border-accent px-4 text-sm font-semibold text-accent transition hover:bg-accent/10 disabled:cursor-not-allowed disabled:opacity-60"
                  disabled={Boolean(loading) || !payload.topic.trim()}
                  type="button"
                  onClick={() => void runFramework()}
                >
                  {loading === "framework" ? <Loader2 size={18} className="animate-spin" aria-hidden="true" /> : <Workflow size={18} aria-hidden="true" />}
                  Khung chuyên sâu
                </button>
              </div>
            </div>

            {error ? <p className="rounded border border-red-400/30 bg-red-400/10 p-3 text-sm text-red-200">{error}</p> : null}
          </form>

          <OutputPanel latestFile={latestFile} generatedFiles={generatedFiles} />

          {logs.length ? <AgentRunList logs={logs} /> : null}
        </aside>

        <main className="min-w-0 space-y-6">
          {loading === "framework" || frameworkLogs.length ? (
            <FrameworkProgressPanel
              logs={frameworkLogs}
              loading={loading === "framework"}
              elapsedSeconds={frameworkStartedAt ? Math.max(0, Math.floor((Date.now() - frameworkStartedAt) / 1000) + progressTick * 0) : 0}
              averageScore={frameworkAverageScore}
              agentScores={frameworkScores}
              files={generatedFiles}
            />
          ) : (
            <ResearchEmptyState />
          )}

          <section className="min-w-0 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-sm font-semibold text-white">Markdown preview</h2>
                <p className="mt-1 text-xs text-slate-400">Nội dung map hoặc note mới nhất.</p>
              </div>
              {markdown ? (
                <span className="rounded border border-line bg-panel px-2.5 py-1 text-xs text-slate-300">
                  {markdown.split("\n").length} dòng
                </span>
              ) : null}
            </div>
            <MarkdownPreview content={markdown} />
          </section>
        </main>
      </div>
    </div>
  );
}

function MetricTile({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: string }) {
  return (
    <div className="rounded border border-line bg-ink px-3 py-2">
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Icon size={14} className="text-signal" aria-hidden="true" />
        {label}
      </div>
      <div className="mt-1 text-lg font-semibold text-white">{value}</div>
    </div>
  );
}

function OutputPanel({ latestFile, generatedFiles }: { latestFile: string | null; generatedFiles: string[] }) {
  if (!latestFile && !generatedFiles.length) return null;
  return (
    <section className="rounded border border-line bg-panel p-4 shadow-soft">
      <div className="flex items-center gap-2 text-sm font-semibold text-white">
        <FileText size={16} className="text-signal" aria-hidden="true" />
        Output
      </div>
      {latestFile ? (
        <div className="mt-3 rounded border border-line bg-ink p-3 text-xs text-slate-300">
          <div className="mb-1 text-slate-500">File chính</div>
          <div className="truncate">{latestFile}</div>
        </div>
      ) : null}
      {generatedFiles.length ? (
        <div className="mt-3">
          <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Shard Markdown</div>
          <div className="max-h-44 space-y-1 overflow-auto pr-1 scrollbar-thin">
            {generatedFiles.map((file) => (
              <div key={file} className="truncate rounded border border-line bg-ink px-2 py-1.5 text-xs text-slate-300">
                {file}
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </section>
  );
}

function AgentRunList({ logs }: { logs: AgentLog[] }) {
  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold text-white">Agent run</h2>
        <span className="text-xs text-slate-500">{logs.length} log</span>
      </div>
      <div className="max-h-[540px] space-y-3 overflow-auto pr-1 scrollbar-thin">
        {logs.map((log) => (
          <AgentStatusCard
            key={`${log.agent}-${log.message}`}
            agent={log.agent}
            status={log.status}
            message={log.message}
            score={log.score}
            runtimeMs={log.runtime_ms}
          />
        ))}
      </div>
    </section>
  );
}

function ResearchEmptyState() {
  return (
    <section className="rounded border border-dashed border-line bg-panel p-6 shadow-soft">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="min-w-0">
          <div className="inline-flex h-10 w-10 items-center justify-center rounded border border-signal/30 bg-signal/10 text-signal">
            <Workflow size={20} aria-hidden="true" />
          </div>
          <h2 className="mt-4 text-lg font-semibold text-white">Mini map xử lý</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Chạy khung chuyên sâu để xem plan, search query, chất lượng nguồn, worker lanes, synthesis, filter và cây map Markdown.
          </p>
        </div>
        <div className="grid min-w-[220px] gap-2 text-xs text-slate-400">
          {flowStages.slice(0, 4).map((stage) => (
            <div key={stage.id} className="flex items-center gap-2 rounded border border-line bg-ink px-3 py-2">
              <stage.icon size={14} className={stage.iconClass} aria-hidden="true" />
              <span>{stage.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

interface FlowStage {
  id: string;
  label: string;
  data: string;
  icon: LucideIcon;
  iconClass: string;
  activeClass: string;
  barClass: string;
}

const flowStages: FlowStage[] = [
  {
    id: "plan",
    label: "Plan",
    data: "Yêu cầu + tiêu chí",
    icon: BrainCircuit,
    iconClass: "text-signal",
    activeClass: "border-signal/50 bg-signal/10",
    barClass: "bg-signal"
  },
  {
    id: "search",
    label: "Search",
    data: "Query + nguồn",
    icon: Search,
    iconClass: "text-accent",
    activeClass: "border-accent/50 bg-accent/10",
    barClass: "bg-accent"
  },
  {
    id: "quality",
    label: "Quality",
    data: "Trust + reject",
    icon: ShieldCheck,
    iconClass: "text-amber-300",
    activeClass: "border-amber-300/50 bg-amber-300/10",
    barClass: "bg-amber-300"
  },
  {
    id: "route",
    label: "Route",
    data: "Worker packets",
    icon: Route,
    iconClass: "text-cyan-300",
    activeClass: "border-cyan-300/50 bg-cyan-300/10",
    barClass: "bg-cyan-300"
  },
  {
    id: "worker",
    label: "Workers",
    data: "Crawl/Clean/Extract",
    icon: Network,
    iconClass: "text-emerald-300",
    activeClass: "border-emerald-300/50 bg-emerald-300/10",
    barClass: "bg-emerald-300"
  },
  {
    id: "synthesize",
    label: "Synthesis",
    data: "Hợp nhất",
    icon: Layers3,
    iconClass: "text-sky-300",
    activeClass: "border-sky-300/50 bg-sky-300/10",
    barClass: "bg-sky-300"
  },
  {
    id: "filter",
    label: "Filter",
    data: "Dữ liệu sạch",
    icon: Filter,
    iconClass: "text-lime-300",
    activeClass: "border-lime-300/50 bg-lime-300/10",
    barClass: "bg-lime-300"
  },
  {
    id: "map",
    label: "Map",
    data: "Markdown tree",
    icon: Database,
    iconClass: "text-teal-300",
    activeClass: "border-teal-300/50 bg-teal-300/10",
    barClass: "bg-teal-300"
  }
];

function FrameworkProgressPanel({
  logs,
  loading,
  elapsedSeconds,
  averageScore,
  agentScores,
  files
}: {
  logs: AgentLog[];
  loading: boolean;
  elapsedSeconds: number;
  averageScore: number | null;
  agentScores: Record<string, number>;
  files: string[];
}) {
  const completedStages = new Set(logs.map((log) => log.stage).filter((stage): stage is string => Boolean(stage)));
  const estimatedIndex = loading ? Math.min(flowStages.length - 1, Math.floor(elapsedSeconds / 4)) : flowStages.length;
  const finishedCount = loading ? Math.max(completedStages.size, estimatedIndex + 1) : completedStages.size;
  const progressPercent = Math.min(100, Math.round((finishedCount / flowStages.length) * 100));
  const timeline = logs.length ? logs : makeEstimatedLogs(estimatedIndex);
  const scores = Object.entries(agentScores).sort((left, right) => right[1] - left[1]);
  const detailStages = flowStages
    .map((stage) => ({ ...stage, logs: logs.filter((log) => log.stage === stage.id) }))
    .filter((stage) => stage.logs.length > 0);
  const routePackets = logs.flatMap((log) => (log.stage === "route" ? asPackets(log.data?.packets) : []));
  const workerLogs = logs.filter((log) => log.stage === "worker");
  const acceptedSources = countSourcesByField(logs, "accepted_sources");
  const rejectedSources = countSourcesByField(logs, "rejected_sources") + countSourcesByField(logs, "dropped_sources");
  const allSources = countSources(logs);
  const avgStageScore = averageScore ?? averageLogScore(logs);

  return (
    <section className="rounded border border-line bg-panel p-5 shadow-soft">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-2 rounded border border-signal/30 bg-signal/10 px-2.5 py-1 text-xs font-semibold text-signal">
              <Workflow size={14} aria-hidden="true" />
              Mini map xử lý
            </span>
            {loading ? (
              <span className="inline-flex items-center gap-2 rounded border border-accent/30 bg-accent/10 px-2.5 py-1 text-xs font-medium text-accent">
                <Loader2 size={14} className="animate-spin" aria-hidden="true" />
                Đang chạy
              </span>
            ) : null}
          </div>
          <h2 className="mt-3 text-lg font-semibold text-white">Research flow cockpit</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
            Theo dõi từng bước agent đã lập plan gì, search nguồn nào, lọc chất lượng ra sao và map tri thức được ghi ở đâu.
          </p>
        </div>
        <div className="grid w-full gap-2 sm:grid-cols-4 xl:w-[520px]">
          <MiniStat icon={Gauge} label="Điểm TB" value={avgStageScore != null ? `${Math.round(avgStageScore * 100)}%` : loading ? "..." : "N/A"} />
          <MiniStat icon={Search} label="Nguồn" value={String(allSources)} />
          <MiniStat icon={ShieldCheck} label="Giữ/loại" value={`${acceptedSources}/${rejectedSources}`} />
          <MiniStat icon={FileText} label="Files" value={String(files.length)} />
        </div>
      </div>

      <div className="mt-4 h-2 overflow-hidden rounded bg-ink">
        <div className="h-full rounded bg-accent transition-all duration-500" style={{ width: `${progressPercent}%` }} />
      </div>
      <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
        <span>{progressPercent}% hoàn tất</span>
        <span>{elapsedSeconds ? `${elapsedSeconds}s` : loading ? "0s" : "xong"}</span>
      </div>

      <div className="mt-5">
        <DataFlowCanvas completedStages={completedStages} estimatedIndex={estimatedIndex} loading={loading} logs={logs} />
      </div>

      <div className="mt-5 grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-4">
          <WorkerSwimlanes logs={workerLogs} packets={routePackets} loading={loading} />

          {detailStages.length ? (
            <div className="rounded border border-line bg-ink/70 p-4">
              <div className="mb-3 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                  <FileSearch size={14} aria-hidden="true" />
                  Chi tiết nghiên cứu
                </div>
                <span className="text-xs text-slate-500">{detailStages.length} stage có log</span>
              </div>
              <div className="space-y-3">
                {detailStages.map((stage) => (
                  <StageTraceCard key={stage.id} stage={stage} />
                ))}
              </div>
            </div>
          ) : null}
        </div>

        <div className="space-y-4">
          <TimelinePanel timeline={timeline} />
          {scores.length ? <ScorePanel scores={scores} /> : null}
        </div>
      </div>
    </section>
  );
}

function MiniStat({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: string }) {
  return (
    <div className="rounded border border-line bg-ink px-3 py-2">
      <div className="flex items-center gap-2 text-[11px] uppercase tracking-wide text-slate-500">
        <Icon size={13} className="text-signal" aria-hidden="true" />
        {label}
      </div>
      <div className="mt-1 text-sm font-semibold text-white">{value}</div>
    </div>
  );
}

function DataFlowCanvas({
  completedStages,
  estimatedIndex,
  loading,
  logs
}: {
  completedStages: Set<string>;
  estimatedIndex: number;
  loading: boolean;
  logs: AgentLog[];
}) {
  return (
    <div className="overflow-x-auto rounded border border-line bg-ink/70 p-3 scrollbar-thin">
      <div className="grid min-w-[1120px] grid-cols-[repeat(8,minmax(124px,1fr))] gap-2">
        {flowStages.map((stage, index) => {
          const StageIcon = stage.icon;
          const stageLogs = logs.filter((log) => log.stage === stage.id);
          const done = completedStages.has(stage.id);
          const active = loading && !done && index === estimatedIndex;
          const muted = !done && !active;
          const score = averageLogScore(stageLogs);
          return (
            <div key={stage.id} className="relative">
              <div
                className={[
                  "min-h-[132px] rounded border p-3 transition",
                  done || active ? stage.activeClass : "border-line bg-panel",
                  active ? "ring-1 ring-signal/60" : "",
                  muted ? "opacity-70" : ""
                ].join(" ")}
              >
                <div className="flex items-start justify-between gap-2">
                  <span className={["inline-flex h-8 w-8 items-center justify-center rounded border border-line bg-ink", stage.iconClass].join(" ")}>
                    <StageIcon size={16} aria-hidden="true" />
                  </span>
                  {active ? (
                    <Loader2 size={15} className="animate-spin text-signal" aria-hidden="true" />
                  ) : (
                    <span className={["h-2.5 w-2.5 rounded-full", done ? stage.barClass : "bg-slate-600"].join(" ")} />
                  )}
                </div>
                <div className="mt-3 min-w-0">
                  <div className="truncate text-sm font-semibold text-white">{stage.label}</div>
                  <div className="mt-1 text-xs text-slate-400">{stage.data}</div>
                </div>
                <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] text-slate-500">
                  <div className="rounded border border-line bg-ink px-2 py-1">
                    <div>Events</div>
                    <div className="font-semibold text-slate-200">{stageLogs.length || (active ? "..." : 0)}</div>
                  </div>
                  <div className="rounded border border-line bg-ink px-2 py-1">
                    <div>Score</div>
                    <div className="font-semibold text-slate-200">{score != null ? `${Math.round(score * 100)}%` : active ? "..." : "N/A"}</div>
                  </div>
                </div>
                <div className="mt-2 truncate text-[11px] text-slate-500">{stageSummary(stage.id, stageLogs)}</div>
              </div>
              {index < flowStages.length - 1 ? (
                <div className="pointer-events-none absolute -right-3 top-1/2 z-10 hidden -translate-y-1/2 rounded-full border border-line bg-ink p-1 text-slate-500 xl:block">
                  <ArrowRight size={14} aria-hidden="true" />
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function WorkerSwimlanes({ logs, packets, loading }: { logs: AgentLog[]; packets: TracePacket[]; loading: boolean }) {
  const lanes = buildWorkerLanes(logs, packets, loading);
  if (!lanes.length) return null;
  return (
    <section className="rounded border border-line bg-ink/70 p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
          <Network size={14} aria-hidden="true" />
          Worker lanes
        </div>
        <span className="text-xs text-slate-500">{lanes.length} lane</span>
      </div>
      <div className="grid gap-3 lg:grid-cols-2">
        {lanes.map((lane) => (
          <article key={lane.key} className="rounded border border-line bg-panel p-3">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="truncate text-sm font-semibold text-white">{lane.title}</div>
                <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-400">{lane.focus}</p>
              </div>
              <span className="shrink-0 rounded border border-accent/30 bg-accent/10 px-2 py-1 text-xs font-semibold text-accent">
                {lane.score != null ? `${Math.round(lane.score * 100)}%` : "..."}
              </span>
            </div>
            <div className="mt-3 grid grid-cols-3 gap-2 text-[11px] text-slate-500">
              <div className="rounded border border-line bg-ink px-2 py-1">
                <div>Input</div>
                <div className="font-semibold text-slate-200">{lane.input ?? lane.sources.length}</div>
              </div>
              <div className="rounded border border-line bg-ink px-2 py-1">
                <div>Output</div>
                <div className="font-semibold text-slate-200">{lane.output ?? "..."}</div>
              </div>
              <div className="rounded border border-line bg-ink px-2 py-1">
                <div>Time</div>
                <div className="font-semibold text-slate-200">{lane.runtime ?? "..."}</div>
              </div>
            </div>
            {lane.sources.length ? (
              <div className="mt-3 space-y-1">
                {lane.sources.slice(0, 3).map((source, index) => (
                  <div key={`${source.url}-${index}`} className="truncate rounded border border-line bg-ink px-2 py-1 text-xs text-slate-400">
                    {source.title || source.url}
                  </div>
                ))}
              </div>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}

function TimelinePanel({ timeline }: { timeline: AgentLog[] }) {
  return (
    <section className="rounded border border-line bg-ink/70 p-4">
      <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
        <Clock3 size={14} aria-hidden="true" />
        Timeline agent
      </div>
      <div className="max-h-[460px] space-y-2 overflow-auto pr-1 scrollbar-thin">
        {timeline.map((log, index) => (
          <div key={`${log.agent}-${index}`} className="grid grid-cols-[16px_minmax(0,1fr)_auto] gap-2 rounded border border-line bg-panel p-3">
            <div className="pt-1">
              <span className={["block h-3 w-3 rounded-full", log.status === "success" ? "bg-accent" : log.status === "running" ? "bg-signal" : "bg-slate-600"].join(" ")} />
            </div>
            <div className="min-w-0">
              <div className="truncate text-xs font-semibold text-white">{log.agent}</div>
              <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-400">{log.message}</p>
              <div className="mt-2 flex flex-wrap gap-2 text-[11px] text-slate-500">
                {log.input_count != null ? <span>in {log.input_count}</span> : null}
                {log.output_count != null ? <span>out {log.output_count}</span> : null}
                {log.runtime_ms != null ? <span>{formatRuntime(log.runtime_ms)}</span> : null}
              </div>
            </div>
            <div className="text-right text-xs">
              <div className="font-semibold text-accent">{log.score != null ? `${Math.round(log.score * 100)}%` : "..."}</div>
              <div className="mt-1 text-slate-500">{log.stage ?? "stage"}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function ScorePanel({ scores }: { scores: [string, number][] }) {
  return (
    <section className="rounded border border-line bg-ink/70 p-4">
      <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
        <Gauge size={14} aria-hidden="true" />
        Điểm từng tác nhân
      </div>
      <div className="space-y-3">
        {scores.slice(0, 10).map(([agent, score]) => (
          <div key={agent} className="text-xs">
            <div className="grid grid-cols-[minmax(0,1fr)_44px] items-center gap-3">
              <span className="truncate text-slate-300">{agent}</span>
              <span className="text-right font-semibold text-white">{Math.round(score * 100)}%</span>
            </div>
            <div className="mt-1.5 h-1.5 overflow-hidden rounded bg-panel">
              <div className="h-full rounded bg-signal" style={{ width: `${Math.round(score * 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function StageTraceCard({ stage }: { stage: { id: string; label: string; logs: AgentLog[] } }) {
  return (
    <div className="rounded border border-line bg-panel p-3">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-white">{stage.label}</h3>
        <span className="text-xs text-slate-500">{stage.logs.length} bước</span>
      </div>
      <div className="mt-3 space-y-3">{stage.logs.map((log, index) => renderStageDetail(stage.id, log, index))}</div>
    </div>
  );
}

function renderStageDetail(stageId: string, log: AgentLog, index: number) {
  const data = log.data ?? {};
  if (stageId === "plan") {
    return (
      <TraceBlock key={index} title={log.message}>
        <TracePill label="Profile" value={asText(data.profile_name)} />
        <TracePill label="Worker" value={asText(data.worker_count)} />
        <TracePill label="Song song" value={asText(data.max_parallel_workers)} />
        <TraceList title="Trọng tâm" items={asStringList(data.focus_areas)} />
        <TraceList title="Query sẽ chạy" items={asStringList(data.queries)} />
      </TraceBlock>
    );
  }

  if (stageId === "search") {
    return (
      <TraceBlock key={index} title={asText(data.query) || log.message}>
        <TraceSourceList title="Nguồn tìm thấy" sources={asSources(data.sources)} />
      </TraceBlock>
    );
  }

  if (stageId === "quality") {
    return (
      <TraceBlock key={index} title={log.message}>
        <TraceList title="Domain ưu tiên" items={asStringList(data.trusted_domains)} />
        <TraceSourceList title="Nguồn được nhận" sources={asSources(data.accepted_sources)} />
        <TraceSourceList title="Nguồn bị loại" sources={asSources(data.rejected_sources)} showReason />
      </TraceBlock>
    );
  }

  if (stageId === "route") {
    return (
      <TraceBlock key={index} title={log.message}>
        <TracePacketList packets={asPackets(data.packets)} />
      </TraceBlock>
    );
  }

  if (stageId === "worker") {
    return (
      <TraceBlock key={index} title={`${log.agent}: ${asText(data.focus) || "worker lane"}`}>
        <TracePill label="Input" value={asText(log.input_count)} />
        <TracePill label="Output" value={asText(log.output_count)} />
        <TracePill label="Runtime" value={log.runtime_ms != null ? formatRuntime(log.runtime_ms) : "N/A"} />
        <TraceSourceList title="Nguồn worker quét" sources={asSources(data.sources)} />
        <TraceDocumentList documents={asDocuments(data.cleaned_previews ?? data.cleaned_documents)} />
        <TraceCritiqueList critiques={asCritiques(data.critiques)} />
      </TraceBlock>
    );
  }

  if (stageId === "synthesize") {
    return (
      <TraceBlock key={index} title={log.message}>
        <TracePill label="Nguồn" value={asText(data.source_count)} />
        <TracePill label="Đã clean" value={asText(data.cleaned_count)} />
        <TracePill label="Extract" value={asText(data.extracted_count)} />
        <TraceList title="Nguồn đã gom" items={asStringList(data.source_titles)} />
        <TraceList title="Khái niệm nổi bật" items={asStringList(data.top_concepts)} />
      </TraceBlock>
    );
  }

  if (stageId === "filter") {
    return (
      <TraceBlock key={index} title={log.message}>
        <TracePill label="Trust TB" value={asText(data.average_trust)} />
        <TracePill label="Ngưỡng" value={asText(data.min_trust_score)} />
        <TraceList title="URL giữ lại" items={asStringList(data.kept_urls)} />
        <TraceRejectList rejected={asRejected(data.dropped_sources)} />
      </TraceBlock>
    );
  }

  if (stageId === "map") {
    return (
      <TraceBlock key={index} title={log.message}>
        <TracePill label="Map" value={asText(data.map_file)} />
        <TracePill label="Chunks" value={asText(data.indexed_chunks)} />
        <TraceList title="File đã ghi" items={asStringList(data.generated_files)} />
      </TraceBlock>
    );
  }

  return (
    <TraceBlock key={index} title={log.message}>
      <pre className="overflow-auto rounded bg-black/20 p-2 text-xs text-slate-300">{JSON.stringify(data, null, 2)}</pre>
    </TraceBlock>
  );
}

function TraceBlock({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded border border-line/80 bg-panel/50 p-3">
      <div className="text-xs font-semibold text-slate-200">{title}</div>
      <div className="mt-3 flex flex-wrap gap-2">{children}</div>
    </div>
  );
}

function TracePill({ label, value }: { label: string; value: string }) {
  if (!value) return null;
  return (
    <span className="rounded border border-line bg-ink px-2 py-1 text-xs text-slate-300">
      {label}: <span className="text-white">{value}</span>
    </span>
  );
}

function TraceList({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <div className="w-full">
      <div className="mb-1 text-xs font-medium text-slate-300">{title}</div>
      <div className="space-y-1">
        {items.slice(0, 8).map((item, index) => (
          <div key={`${item}-${index}`} className="rounded border border-line bg-ink px-2 py-1 text-xs text-slate-400">
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}

function TraceSourceList({ title, sources, showReason = false }: { title: string; sources: TraceSource[]; showReason?: boolean }) {
  if (!sources.length) return null;
  return (
    <div className="w-full">
      <div className="mb-1 text-xs font-medium text-slate-300">{title}</div>
      <div className="space-y-1">
        {sources.slice(0, 8).map((source, index) => (
          <div key={`${source.url}-${index}`} className="rounded border border-line bg-ink px-2 py-2 text-xs">
            <div className="truncate text-slate-200">{source.title || source.url}</div>
            <div className="truncate text-slate-500">{source.url}</div>
            {showReason && source.reason ? <div className="mt-1 text-amber-300">{source.reason}</div> : null}
          </div>
        ))}
      </div>
    </div>
  );
}

function TracePacketList({ packets }: { packets: TracePacket[] }) {
  if (!packets.length) return null;
  return (
    <div className="w-full space-y-1">
      {packets.map((packet) => (
        <div key={packet.worker_id} className="rounded border border-line bg-ink px-2 py-2 text-xs">
          <div className="font-medium text-slate-200">
            Worker {packet.worker_id}: {packet.focus} ({packet.source_count} nguồn)
          </div>
          {packet.sources.slice(0, 3).map((source, index) => (
            <div key={`${source.url}-${index}`} className="mt-1 truncate text-slate-500">
              {source.title || source.url}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function TraceDocumentList({ documents }: { documents: TraceDocument[] }) {
  if (!documents.length) return null;
  return (
    <div className="w-full">
      <div className="mb-1 text-xs font-medium text-slate-300">Data đã clean</div>
      <div className="space-y-1">
        {documents.map((document, index) => (
          <div key={`${document.url}-${index}`} className="rounded border border-line bg-ink px-2 py-2 text-xs">
            <div className="truncate text-slate-200">{document.title || document.url}</div>
            <div className="text-slate-500">{document.content_length} ký tự</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TraceCritiqueList({ critiques }: { critiques: TraceCritique[] }) {
  if (!critiques.length) return null;
  return (
    <div className="w-full">
      <div className="mb-1 text-xs font-medium text-slate-300">Đánh giá nguồn</div>
      <div className="space-y-1">
        {critiques.map((critique, index) => (
          <div key={`${critique.url}-${index}`} className="rounded border border-line bg-ink px-2 py-2 text-xs">
            <div className="truncate text-slate-500">{critique.url}</div>
            <div className="mt-1 text-slate-300">
              {critique.trust_level || "unknown"} · {critique.trust_score ?? "N/A"} · {critique.reason || "Không có lý do"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TraceRejectList({ rejected }: { rejected: TraceRejected[] }) {
  if (!rejected.length) return null;
  return (
    <div className="w-full">
      <div className="mb-1 text-xs font-medium text-slate-300">Nguồn bị filter</div>
      <div className="space-y-1">
        {rejected.map((item, index) => (
          <div key={`${item.url}-${index}`} className="rounded border border-line bg-ink px-2 py-2 text-xs">
            <div className="truncate text-slate-500">{item.url}</div>
            <div className="mt-1 text-amber-300">{item.reason}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

interface WorkerLane {
  key: string;
  title: string;
  focus: string;
  sources: TraceSource[];
  score?: number | null;
  input?: number | null;
  output?: number | null;
  runtime?: string;
}

function buildWorkerLanes(logs: AgentLog[], packets: TracePacket[], loading: boolean): WorkerLane[] {
  if (logs.length) {
    return logs.map((log, index) => ({
      key: `${log.agent}-${index}`,
      title: log.agent,
      focus: asText(log.data.focus) || log.message || "Worker lane",
      sources: asSources(log.data.sources),
      score: log.score,
      input: log.input_count,
      output: log.output_count,
      runtime: log.runtime_ms != null ? formatRuntime(log.runtime_ms) : undefined
    }));
  }

  if (packets.length) {
    return packets.map((packet) => ({
      key: `packet-${packet.worker_id}`,
      title: `Worker ${packet.worker_id}`,
      focus: packet.focus || "Worker packet",
      sources: packet.sources,
      score: null,
      input: packet.source_count,
      output: null
    }));
  }

  if (!loading) return [];
  return ["overview", "core concepts", "workflow", "risks"].map((focus, index) => ({
    key: `placeholder-${focus}`,
    title: `Worker ${index + 1}`,
    focus,
    sources: [],
    score: null,
    input: null,
    output: null
  }));
}

function averageLogScore(logs: AgentLog[]) {
  const scores = logs.map((log) => log.score).filter((score): score is number => typeof score === "number");
  if (!scores.length) return null;
  return scores.reduce((total, score) => total + score, 0) / scores.length;
}

function countSources(logs: AgentLog[]) {
  const urls = new Set<string>();
  logs.forEach((log) => {
    collectUrls(urls, log.data.sources);
    collectUrls(urls, log.data.accepted_sources);
    collectUrls(urls, log.data.rejected_sources);
    collectUrls(urls, log.data.dropped_sources);
    asPackets(log.data.packets).forEach((packet) => collectUrls(urls, packet.sources));
  });
  return urls.size;
}

function countSourcesByField(logs: AgentLog[], field: string) {
  const urls = new Set<string>();
  logs.forEach((log) => collectUrls(urls, log.data[field]));
  return urls.size;
}

function collectUrls(urls: Set<string>, value: unknown) {
  if (!Array.isArray(value)) return;
  value.forEach((item) => {
    if (typeof item === "string" && item.trim()) {
      urls.add(item.trim());
      return;
    }
    if (item && typeof item === "object") {
      const url = asText((item as Record<string, unknown>).url);
      if (url) urls.add(url);
    }
  });
}

function stageSummary(stageId: string, logs: AgentLog[]) {
  if (!logs.length) return "Chưa có log";
  const data = logs[0].data;
  if (stageId === "plan") return `${asText(data.profile_name) || "Auto profile"} · ${asStringList(data.queries).length} query`;
  if (stageId === "search") return `${countSourcesByField(logs, "sources")} nguồn tìm thấy`;
  if (stageId === "quality") return `${countSourcesByField(logs, "accepted_sources")} giữ · ${countSourcesByField(logs, "rejected_sources")} loại`;
  if (stageId === "route") return `${asPackets(data.packets).length} worker packet`;
  if (stageId === "worker") return `${logs.length} lane · ${logs.reduce((total, log) => total + (log.output_count ?? 0), 0)} output`;
  if (stageId === "synthesize") return `${asText(data.extracted_count) || "0"} extract · ${asStringList(data.top_concepts).length} concept`;
  if (stageId === "filter") return `Trust TB ${asText(data.average_trust) || "N/A"}`;
  if (stageId === "map") return `${asStringList(data.generated_files).length} file · ${asText(data.indexed_chunks) || "0"} chunk`;
  return logs[0].message;
}

function makeEstimatedLogs(activeIndex: number): AgentLog[] {
  return flowStages.slice(0, activeIndex + 1).map((stage, index) => ({
    agent: `Framework${stage.label}Agent`,
    status: index === activeIndex ? "running" : "success",
    message: index === activeIndex ? `Đang xử lý ${stage.data.toLowerCase()}` : `Đã xử lý ${stage.data.toLowerCase()}`,
    stage: stage.id,
    score: index === activeIndex ? null : 1,
    data: {}
  }));
}

function formatRuntime(value: number) {
  if (value < 1000) return `${value}ms`;
  return `${(value / 1000).toFixed(1)}s`;
}

interface TraceSource {
  title?: string;
  url?: string;
  snippet?: string;
  reason?: string;
}

interface TracePacket {
  worker_id: number;
  focus: string;
  source_count: number;
  sources: TraceSource[];
}

interface TraceDocument {
  title?: string;
  url?: string;
  content_length?: number;
}

interface TraceCritique {
  url?: string;
  trust_level?: string;
  trust_score?: number;
  reason?: string;
}

interface TraceRejected {
  url?: string;
  reason?: string;
}

function asText(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return "";
}

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => asText(item)).filter(Boolean);
}

function asSources(value: unknown): TraceSource[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object")
    .map((item) => ({
      title: asText(item.title),
      url: asText(item.url),
      snippet: asText(item.snippet),
      reason: asText(item.reason)
    }));
}

function asPackets(value: unknown): TracePacket[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object")
    .map((item) => ({
      worker_id: Number(item.worker_id ?? 0),
      focus: asText(item.focus),
      source_count: Number(item.source_count ?? 0),
      sources: asSources(item.sources)
    }));
}

function asDocuments(value: unknown): TraceDocument[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object")
    .map((item) => ({
      title: asText(item.title),
      url: asText(item.url),
      content_length: Number(item.content_length ?? 0)
    }));
}

function asCritiques(value: unknown): TraceCritique[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object")
    .map((item) => ({
      url: asText(item.url),
      trust_level: asText(item.trust_level),
      trust_score: item.trust_score == null ? undefined : Number(item.trust_score),
      reason: asText(item.reason)
    }));
}

function asRejected(value: unknown): TraceRejected[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object")
    .map((item) => ({
      url: asText(item.url),
      reason: asText(item.reason)
    }));
}
